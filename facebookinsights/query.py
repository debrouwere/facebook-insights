# encoding: utf-8

import os
import re
import urlparse
from dateutil.parser import parse as parse_date
from facepy import GraphAPI


class Insights(object):
    def __init__(self, raw):
        self.raw = raw


class Selection(object):
    def __init__(self, account):
        self.account = account
        self.graph = account.graph

    def find(self, q):
        return self.graph.find(q, 'post')

    def range(self):
        pass

    def limit(self):
        pass

    def __getitem__(self, key):
        return self.get()[key]

    def __iter__(self):
        if not hasattr(self, '_results'):
            self._results = self.get()
        return self._results.__iter__()

    def get(self):
        data = self.graph.get(self.account.id + '/posts')['data']
        return [Post(self.account, post) for post in data]


class Picture(object):
    def __init__(self, post, raw):
        self.post = post
        self.graph = post.graph
        self.raw = self.url = raw
        self.parsed_url = urlparse.urlparse(self.raw)
        self.qs = urlparse.parse_qs(self.parsed_url.query)
        self.origin = self.qs['url'][0]
        self.basename = self.origin.split('/')[-1]
        self.width = self.qs['w'][0]
        self.height = self.qs['h'][0]

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
        self.id = raw['id']
        self.type = raw['type']
        self.name = raw['name']
        self.created_time = parse_date(raw['created_time'])
        self.updated_time = parse_date(raw['updated_time'])
        self.link = raw.get('link')
        self.description = raw['description']
        self.shares = raw.get('shares')
        # TODO: figure out if *all* comments and likes are included 
        # when getting post data, or just some
        self.comments = getdata(raw, 'comments')
        self.likes = getdata(raw, 'likes')
        QUOTE_PATTERN = ur'[\"\u201c\u201e\u00ab]\s?(.+?)\s?[\"\u201c\u201d\u00bb]'
        self.quotes = re.findall(QUOTE_PATTERN, self.description)
        if raw['picture']:
            self.picture = Picture(self, raw['picture'])
        else:
            self.picture = None

    @property
    def insights(self):
        return self.graph.get(self.id + '/insights')

    def __repr__(self):
        return "<Post: {} ({})>".format(self.id, self.created_time)

# TODO: paging and memoization
class Page(object):
    def __init__(self, graph):
        raw = graph.get('me')
        self.raw = raw
        self.id = raw['id']
        self.name = raw['name']
        self.graph = graph

    @property
    def insights(self):
        return self.graph.get(self.id + '/insights')['data']

    @property
    def posts(self):
        return Selection(self)

    def __repr__(self):
        return "<Page {}: {}>".format(self.id, self.name)
