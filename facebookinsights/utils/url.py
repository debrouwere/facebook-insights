# encoding: utf-8

import requests
try:
    # Python 2
    import urlparse as parse
except ImportError:
    # Python 3
    import urllib.parse as parse

def resolve(url):
    response = requests.head(url, allow_redirects=True)
    return response.url

def base(url):
    base = parse.urlsplit(url)[:3]
    url = parse.urlunsplit(base + ('', ''))
    return url