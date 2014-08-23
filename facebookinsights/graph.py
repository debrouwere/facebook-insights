# encoding: utf-8

import os
import re
import math
import copy
import urlparse
import functools
import pytz
from datetime import datetime
import utils
from utils.api import GraphAPI
from utils.functional import immutable, memoize


class Insights(object):
    def __init__(self, raw):
        self.raw = raw


class Selection(object):
    def __init__(self, edge):
        self.edge = edge
        self.graph = edge.graph
        self.meta = {
            'since': datetime(1, 1, 1, tzinfo=pytz.utc), 
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
    def range(self, since, until=None):
        if not until:
            until = datetime.today().isoformat()

        self.meta['since'] = utils.date.parse_utc(since)
        self.meta['until'] = utils.date.parse_utc(until)
        self.params['page'] = True
        self.params['since'] = utils.date.timestamp(since)
        self.params['until'] = utils.date.timestamp(until)
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
                if post.created_time >= self.meta['since']:
                    posts.append(post)
                else:
                    return posts

        return posts


class InsightsSelection(Selection):
    @immutable
    def daily(self, metrics=None):
        self.params['period'] = 'day'
        return self.metrics(metrics)

    @immutable
    def weekly(self, metrics=None):
        self.params['period'] = 'week'
        return self.metrics(metrics)

    @immutable
    def monthly(self, metrics=None):
        self.params['period'] = 'days_28'
        return self.metrics(metrics)

    @immutable
    def lifetime(self, metrics=None):
        self.params['period'] = 'lifetime'
        return self.metrics(metrics)

    @immutable
    def metrics(self, ids):
        if ids:
            if isinstance(ids, list):
                self.meta['single'] = False
            else:
                self.meta['single'] = True
                ids = [ids]
            self.meta['metrics'] = ids
        return self

    def get(self):
        # by default, Facebook returns three days 
        # worth' of insights data
        if 'until' in self.meta:
            seconds = (self.meta['until'] - self.meta['since']).total_seconds()
            days = math.ceil(seconds / 60 / 60 / 24)
        else:
            days = 3

        # TODO: for large date ranges, chunk them up and request
        # the subranges in a batch request (this is a little bit
        # more complex because multiple metrics are *also* batched
        # and so these two things have to work together)
        if days > 31 * 3:
            raise NotImplementedError(
                "Can only fetch date ranges smaller than 3 months.")

        if 'metrics' in self.meta:
            metrics = []
            for metric in self.meta['metrics']:
                metrics.append({'relative_url': metric})
            insights = self.graph.all('insights', 
                metrics, **self.params)
        else:
            insights = self.graph.get('insights', 
                **self.params)

        # if self.meta['single']: 
        #     unwrap_result
        return insights


class Picture(object):
    def __init__(self, post, raw):
        self.post = post
        self.graph = post.graph
        self.raw = self.url = raw
        self.parsed_url = urlparse.urlparse(self.raw)
        self.qs = urlparse.parse_qs(self.parsed_url.query)
        
        if 'url' in self.qs:
            self.origin = self.qs['url'][0]
            self.width = self.qs['w'][0]
            self.height = self.qs['h'][0]
        else:
            self.origin = self.url

        self.basename = self.origin.split('/')[-1]

    def __repr__(self):
        return "<Picture: {} ({}x{})>".format(
            self.basename, self.width, self.height)


class Post(object):
    def __init__(self, account, raw):
        self.account = account
        self.raw = raw
        # most fields aside from id, type, ctime 
        # and mtime are optional
        self.graph = account.graph.partial(raw['id'])
        self.id = raw['id']
        self.type = raw['type']
        self.created_time = utils.date.parse(raw['created_time'])
        self.updated_time = utils.date.parse(raw['updated_time'])
        self.name = raw.get('name')
        self.story = raw.get('story')
        self.link = raw.get('link')
        self.description = raw.get('description')
        self.shares = raw.get('shares')
        # TODO: figure out if *all* comments and likes are included 
        # when getting post data, or just some
        self.comments = utils.api.getdata(raw, 'comments')
        self.likes = utils.api.getdata(raw, 'likes')
        QUOTE_PATTERN = ur'[\"\u201c\u201e\u00ab]\s?(.+?)\s?[\"\u201c\u201d\u00bb]'
        self.quotes = re.findall(QUOTE_PATTERN, self.description or '')
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

        url = utils.url.resolve(self.link)

        if clean:
            url = utils.url.base(url)

        return url

    def __repr__(self):
        time = self.created_time.date().isoformat()
        return "<Post: {} ({})>".format(self.id, time)


class Page(object):
    def __init__(self, token):
        self.graph = GraphAPI(token).partial('me')
        data = self.graph.get()
        self.raw = data
        self.id = data['id']
        self.name = data['name']

    @property
    def insights(self):
        return InsightsSelection(self)

    @property
    def token(self):
        return self.graph.oauth_token

    @property
    def posts(self):
        return PostSelection(self)

    def __repr__(self):
        return "<Page {}: {}>".format(self.id, self.name)
