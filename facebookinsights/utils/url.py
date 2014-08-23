# encoding: utf-8

import requests
import urlparse

def resolve(url):
    response = requests.head(url, allow_redirects=True)
    return response.url

def base(url):
    base = urlparse.urlsplit(url)[:3]
    url = urlparse.urlunsplit(base + ('', ''))
    return url