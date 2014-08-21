# encoding: utf-8

import os
import re
import urlparse
import time
from dateutil.parser import parse as parse_date
from facepy import GraphAPI


class Insights(object):
    def __init__(self, raw):
        self.raw = raw


class Selection(object):
    def __init__(self, account):
        self.account = account
        self.graph = account.graph
        self.params = {
            'page': False, 
        }

    def since(self, date):
        parsed_date = parse_date(date)
        timestamp = int(time.mktime(parsed_date.timetuple()))
        self.params['page'] = True
        self.params['since'] = timestamp
        return self

    # TODO
    def last(n=1):
        self.params['page'] = True
        return self

    def __getitem__(self, key):
        return self.get()[key]

    def __iter__(self):
        if not hasattr(self, '_results'):
            self._results = self.get()
        return self._results.__iter__()

    def find(self, q):
        return self.graph.find(q, 'post')

    def get(self):
        pages = self.graph.get(self.account.id + '/posts', 
            **self.params)
        if not self.params['page']:
            pages = [pages]

        posts = []
        for page in pages:
            for post in page['data']:
                posts.append(Post(self.account, post))
        return posts


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


def getdata(obj, key, default=None):
    if key in obj:
        return obj[key]['data']
    else:
        return default


class Post(object):
    def __init__(self, account, raw):
        self.account = account
        self.graph = account.graph
        self.raw = raw
        # most fields aside from id, type, ctime 
        # and mtime are optional
        self.id = raw['id']
        self.type = raw['type']
        self.created_time = parse_date(raw['created_time'])
        self.updated_time = parse_date(raw['updated_time'])
        self.name = raw.get('name')
        self.story = raw.get('story')
        self.link = raw.get('link')
        self.description = raw.get('description')
        self.shares = raw.get('shares')
        # TODO: figure out if *all* comments and likes are included 
        # when getting post data, or just some
        self.comments = getdata(raw, 'comments')
        self.likes = getdata(raw, 'likes')
        QUOTE_PATTERN = ur'[\"\u201c\u201e\u00ab]\s?(.+?)\s?[\"\u201c\u201d\u00bb]'
        self.quotes = re.findall(QUOTE_PATTERN, self.description or '')
        if 'picture' in raw:
            self.picture = Picture(self, raw['picture'])
        else:
            self.picture = None

    # TODO: support for granularity (daily, weekly, 28days, lifetime)
    # TODO: better processing of results
    def get_insights(self, granularity=None):
        return self.graph.get(self.id + '/insights')

    def __repr__(self):
        time = self.created_time.date().isoformat()
        return "<Post: {} ({})>".format(self.id, time)

# TODO: paging and memoization
class Page(object):
    def __init__(self, graph):
        raw = graph.get('me')
        self.raw = raw
        self.id = raw['id']
        self.name = raw['name']
        self.graph = graph

    def get_insights(self, granularity=None):
        return self.graph.get(self.id + '/insights')['data']

    @property
    def posts(self):
        return Selection(self)

    def __repr__(self):
        return "<Page {}: {}>".format(self.id, self.name)
