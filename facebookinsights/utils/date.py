# encoding: utf-8

import time
from datetime import datetime
import pytz
from dateutil.parser import parse

UTC = datetime(1, 1, 1, tzinfo=pytz.utc)

def parse_utc(datestring):
    return parse(datestring, default=UTC)

def timestamp(date):
    if isinstance(date, basestring):
        date = parse_utc(date)

    return int(time.mktime(date.timetuple()))