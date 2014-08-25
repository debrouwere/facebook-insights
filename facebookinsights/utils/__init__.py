# encoding: utf-8

import api
import date
import functional
import server
import url

import re
import textwrap


def dedent(string):
    return textwrap.dedent(string).replace('\n', '')

def extract_quotes(string):
    QUOTE_PATTERN = ur'[\"\u201c\u201e\u00ab]\s?(.+?)\s?[\"\u201c\u201d\u00bb]'
    return re.findall(QUOTE_PATTERN, string)