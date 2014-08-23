# encoding: utf-8

import time
import textwrap
import urlparse
from datetime import datetime
import pytz
from dateutil.parser import parse as parse_date
import requests

def single_serve(message=None, port=5000):
    import logging
    from flask import Flask, Response, request

    app = Flask(__name__)

    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    captured = {}

    @app.route('/')
    def main():
        request.environ.get('werkzeug.server.shutdown')()
        captured.update(dict(request.args.items()))
        if message:
            print message
        return Response(message, mimetype='text/plain')

    app.run(port=port)
    return captured


UTC = datetime(1, 1, 1, tzinfo=pytz.utc)

def parse_utc_date(datestring):
    return parse_date(datestring, default=UTC)

def to_timestamp(date):
    return int(time.mktime(date.timetuple()))

def date_to_timestamp(datestring):
    return to_timestamp(parse_utc_date(datestring))


def resolve_url(url):
    response = requests.head(url, allow_redirects=True)
    return response.url

def baseurl(url):
    base = urlparse.urlsplit(url)[:3]
    url = urlparse.urlunsplit(base + ('', ''))
    return url


def dedent(string):
    return textwrap.dedent(string).replace('\n', '')