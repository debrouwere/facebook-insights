# encoding: utf-8

import os
import re
import urlparse
import pytz
from datetime import datetime
import utils
from utils.api import GraphAPI


class Insights(object):
    def __init__(self, raw):
        self.raw = raw


class Selection(object):
    def __init__(self, account):
        self.account = account
        self.graph = account.graph
        self.meta = {
            'since': datetime(1, 1, 1, tzinfo=pytz.utc), 
        }
        self.params = {
            'page': False, 
        }

    def range(self, since, until=None):
        if not until:
            until = datetime.today().isoformat()

        self.meta['since'] = utils.date.parse_utc(since)
        self.params['page'] = True
        self.params['since'] = utils.date.timestamp(since)
        self.params['until'] = utils.date.timestamp(until)
        return self

    def since(self, date):
        return self.range(date)

    def __getitem__(self, key):
        return self.get()[key]

    def __iter__(self):
        if not hasattr(self, '_results'):
            self._results = self.get()
        return self._results.__iter__()


class PostSelection(Selection):
    def latest(self, n=1):
        self.params['limit'] = n
        return self

    def find(self, q):
        return self.graph.find(q, 'post')

    def get(self):
        pages = self.graph.get([self.account.id, 'posts'], 
            **self.params)
        if not self.params['page']:
            pages = [pages]

        posts = []
        for page in pages:
            for post in page['data']:
                post = Post(self.account, post)

                """
                For date ranges, we can't rely on pagination 
                because `since` and `until` parameters serve 
                both as paginators and as range delimiters, 
                so there will always be a next page.
                """
                if post.created_time >= self.meta['since']:
                    posts.append(post)
                else:
                    return posts

        return posts


class InsightsSelection(Selection):
    def get(self):
        insights = self.graph.get([self.account.id, 'insights'])


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
        self.graph = account.graph
        self.raw = raw
        # most fields aside from id, type, ctime 
        # and mtime are optional
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

    # TODO: support for granularity (daily, weekly, 28days, lifetime)
    # TODO: support for date ranges (since and until)
    # TODO: better processing of results
    def get_insight(self, metric, granularity='lifetime'):
        return self.graph.get([self.id, metric, granularity])

    def get_insights(self, granularity=None):
        return self.graph.get([self.id, 'insights'])

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
        self.graph = GraphAPI(token)
        data = self.graph.get('me')
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
