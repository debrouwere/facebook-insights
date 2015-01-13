# encoding: utf-8

import time
import datetime as builtin_datetime
import pytz
from dateutil import parser
from dateutil.relativedelta import relativedelta

UTC = COMMON_ERA = builtin_datetime.datetime(1, 1, 1, tzinfo=pytz.utc).date()

def parse(datestring, utc=False):
    if utc:
        return parser.parse(datestring, default=UTC)
    else:
        return parser.parse(datestring)

def timestamp(date, utc=False):
    if isinstance(date, basestring):
        date = parse(date, utc=utc)

    return int(time.mktime(date.timetuple()))

def datetime(obj, utc=False):
    if obj is None:
        return None
    elif isinstance(obj, builtin_datetime.date):
        return obj
    elif isinstance(obj, basestring):
        return parse(obj, utc=utc)
    else:
        raise ValueError("Can only convert strings into dates, received {}".format(obj.__class__))

def date(obj, utc=False):
    # convert datetime into date if needed
    _date = datetime(obj, utc=utc)
    if hasattr(_date, 'date'):
        return _date.date()
    else:
        return _date

formats = {
    'date': lambda date: date, 
    'iso': lambda date: date.isoformat(), 
    'timestamp': lambda date: timestamp(date, utc=True), 
}

def range(start, stop=None, months=0, days=0, format='date'):
    start = date(start, utc=True)
    stop = date(stop, utc=True)

    if days or months:
        if start:
            stop = start + relativedelta(days=days-1, months=months)
        elif stop:
            start = stop - relativedelta(days=days-1, months=months)
        else:
            raise ValueError("Cannot construct a date range from months or days \
                without specifying start or stop.")
    else:
        stop = stop or start

    if format in formats:
        format = formats[format]
    else:
        raise ValueError("{} is an unrecognized date format. Choose from: {}".format(
            format, ", ".join(formats)))

    return format(start), format(stop)
