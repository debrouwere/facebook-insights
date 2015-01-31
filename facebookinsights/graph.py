# encoding: utf-8

import os
import re
import math
import copy
import functools
from collections import namedtuple
import pytz
from datetime import datetime, timedelta
from . import utils
from .utils.api import GraphAPI
from .utils.functional import immutable, memoize


class Selection(object):
    def __init__(self, edge):
        self.edge = edge
        self.graph = edge.graph
        self.meta = {
            'since': utils.date.COMMON_ERA, 
            'until': datetime.now(), 
        }
        self.params = {
            'page': False, 
        }

    def clone(self):
        selection = self.__class__(self.edge)
        selection.meta = copy.copy(self.meta)
        selection.params = copy.copy(self.params)
        return selection

    @immutable
    def range(self, since=None, until=None, months=0, days=0):
        if not (since or until or days or months):
            raise ValueError()

        if not until:
            until = datetime.today()

        since, until = utils.date.range(since, until, months, days)
        self.meta['since'] = since
        self.meta['until'] = until
        self.params['page'] = True
        # when converting dates to timestamps, the returned timestamp
        # will be for the first second on the date in question; 
        # thus, for an inclusive query (end of day) we add another day
        self.params['since'] = utils.date.timestamp(since, utc=True)
        self.params['until'] = utils.date.timestamp(until + timedelta(days=1), utc=True)
        return self

    @immutable
    def since(self, date):
        return self.range(date)

    def __getitem__(self, key):
        return self.get()[key]

    def __iter__(self):
        if not hasattr(self, '_results'):
            self._results = self.get()
        return self._results.__iter__()


class PostSelection(Selection):
    @immutable
    def latest(self, n=1):
        self.params['limit'] = n
        return self

    def find(self, q):
        return self.graph.find(q, 'post')

    def get(self):
        pages = self.graph.get('posts', **self.params)
        if not self.params['page']:
            pages = [pages]

        posts = []
        for page in pages:
            for post in page['data']:
                post = Post(self.edge, post)

                # For date ranges, we can't rely on pagination 
                # because `since` and `until` parameters serve 
                # both as paginators and as range delimiters, 
                # so there will always be a next page.
                if post.created_time.date() >= self.meta['since']:
                    posts.append(post)
                else:
                    return posts

        return posts


class InsightsSelection(Selection):
    @immutable
    def daily(self, metrics=None):
        self.params['period'] = 'day'
        return self._metrics(metrics)

    @immutable
    def weekly(self, metrics=None):
        self.params['period'] = 'week'
        return self._metrics(metrics)

    @immutable
    def monthly(self, metrics=None):
        self.params['period'] = 'days_28'
        return self._metrics(metrics)

    @immutable
    def lifetime(self, metrics=None):
        self.params['period'] = 'lifetime'
        return self._metrics(metrics)

    def _metrics(self, ids=None):
        if ids:
            if isinstance(ids, list):
                self.meta['single'] = False
            else:
                self.meta['single'] = True
                ids = [ids]
            self.meta['metrics'] = ids
        return self

    @property
    def has_daterange(self):
        return 'since' in self.params or 'until' in self.params

    @property
    def days(self):
        # by default, Facebook returns three days 
        # worth' of insights data
        if self.has_daterange:
            seconds = (self.meta['until'] - self.meta['since']).total_seconds()
            return math.ceil(seconds / 60 / 60 / 24)
        else:
            return 3        

    @property
    def is_valid(self):
        # TODO: investigate whether this applies too when asking for 
        # weekly or monthly metrics (that is, whether the limit is 93
        # result rows or truly 93 days)
        if self.days <= 31 * 3:
            return True
        else:
            return False

    def _get_row_date(self, row):
        end_time = row.get('end_time')

        if end_time:
            end_time = utils.date.parse(end_time)
        else:
            end_time = 'lifetime'  

        return end_time

    def get_raw(self):
        if 'metrics' in self.meta:
            metrics = [{'relative_url': metric} for metric in self.meta['metrics']]
            results = self.graph.all('insights', 
                metrics, **self.params)
        else:
            results = [self.graph.get('insights', 
                **self.params)]

        return results

    def get_rows(self):
        # TODO: for large date ranges, chunk them up and request
        # the subranges in a batch request (this is a little bit
        # more complex because multiple metrics are *also* batched
        # and so these two things have to work together)
        if not self.is_valid:
            raise NotImplementedError(
                "Can only fetch date ranges smaller than 3 months.")

        results = self.get_raw()
        datasets = []
        for result in results:
            datasets.extend(result['data'])

        metrics = set()
        for dataset in datasets:
            metric = dataset['name']
            metrics.add(metric)

        data = {}
        for dataset in datasets:
            metric = dataset['name']
            rows = dataset['values']            
            for row in rows:
                date = self._get_row_date(row)
                value = row['value']
                record = utils.record(metrics)
                period = data.setdefault(date, record)
                period[metric] = value

        fields = set(['end_time']).union(metrics)
        Row = namedtuple('Row', fields)
        return [Row(end_time=time, **values) for time, values in data.items()]

    def get(self):
        results = self.get_rows()
        # when a single metric is requested (and not 
        # wrapped in a list), we return a simplified 
        # data format
        if self.meta.get('single', False):
            metric = self.meta['metrics'][0]
            results = [getattr(row, metric) for row in results]

        # when a lifetime metric is requested, 
        # we can simplify further
        if self.params.get('period') == 'lifetime':
            results = results[0]

        return results

    NESTED_METRICS = (
        'page_fans_online'
    )

    def serialize(self, flat=False, timestamp=False):
        _rows = []
        for row in self.get():
            _row = row._asdict()

            if flat:
                _row = utils.flatten(_row, skip=self.NESTED_METRICS)

            if timestamp:
                end_time = utils.date.timestamp(_row['end_time'])
            else:
                end_time = str(_row['end_time'])

            _row['end_time'] = end_time
            _rows.append(_row)

        return _rows

    def __repr__(self):
        if 'metrics' in self.meta:
            metrics = ", ".join(self.meta['metrics'])
        else:
            metrics = 'all available metrics'

        if self.has_daterange:
            date = ' from {} to {}'.format(
                self.meta['since'].date().isoformat(), 
                self.meta['until'].date().isoformat(), 
                )
        else:
            date = ''

        return u"<Insights for '{}' ({}{})>".format(
            repr(self.edge.name), metrics, date)
        

class Picture(object):
    def __init__(self, post, raw):
        self.post = post
        self.graph = post.graph
        self.raw = self.url = raw
        self.parsed_url = utils.url.parse.urlparse(self.raw)
        self.qs = utils.url.parse.parse_qs(self.parsed_url.query)
        
        if 'url' in self.qs:
            self.origin = self.qs['url'][0]
            self.width = self.qs['w'][0]
            self.height = self.qs['h'][0]
        else:
            self.origin = self.url
            self.width = None
            self.height = None

        self.basename = self.origin.split('/')[-1]

    def __repr__(self):
        if self.width and self.height:
            dimensions = ' ({}x{})'.format(self.width, self.height)
        else:
            dimensions = ''

        return u"<Picture: {name}{dimensions}>".format(
            name=self.basename, 
            dimensions=dimensions, 
        )


class Post(object):
    def __init__(self, page, raw):
        self.page = page
        self.raw = raw
        # most fields aside from id, type, ctime 
        # and mtime are optional
        self.graph = page.graph.partial(raw['id'])
        self.id = raw['id']
        self.type = raw['type']
        self.created_time = utils.date.parse(raw['created_time'])
        self.updated_time = utils.date.parse(raw['updated_time'])
        self.name = raw.get('name')
        self.story = raw.get('story')
        self.link = raw.get('link')
        self.message = raw.get('message')
        self.description = raw.get('description')
        self.shares = raw.get('shares')
        # TODO: figure out if *all* comments and likes are included 
        # when getting post data, or just some
        self.comments = utils.api.getdata(raw, 'comments')
        self.likes = utils.api.getdata(raw, 'likes')
        self.quotes = \
            utils.extract_quotes(self.message or '') + \
            utils.extract_quotes(self.description or '')
        # `self.link` is part of Facebook's post schema
        # `self.links` extracts links from the message and 
        # the description of any embedded media
        self.links = set(
            utils.extract_links(self.message or '') + \
            utils.extract_links(self.description or '')
            )
        if self.link:
            self.links.add(self.link)

        if 'picture' in raw:
            self.picture = Picture(self, raw['picture'])
        else:
            self.picture = None

    @property
    def insights(self):
        return InsightsSelection(self)

    def resolve_link(self, clean=False):
        if not self.link:
            return None

        link = utils.url.resolve(self.link)

        if clean:
            return utils.url.base(link)
        else:
            return link

    def resolve_links(self, clean=False):
        links = set([utils.url.resolve(link) for link in self.links])
        if clean:
            return set([utils.url.base(link) for link in links])
        else:
            return links

    def __repr__(self):
        time = self.created_time.date().isoformat()
        return u"<Post: {} ({})>".format(self.id, time)


class Page(object):
    def __init__(self, token):
        self.graph = GraphAPI(token).partial('me')
        data = self.graph.get()
        self.raw = data
        self.id = data['id']
        self.username = data['username']
        self.name = data['name']
        self.link = data.get('link')

    @property
    def token(self):
        return self.graph.oauth_token

    @property
    def insights(self):
        return InsightsSelection(self)

    @property
    def posts(self):
        return PostSelection(self)

    def __repr__(self):
        return u"<Page {}: {}>".format(self.id, self.name)
