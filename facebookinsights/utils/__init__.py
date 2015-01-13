# encoding: utf-8

import api
import date
import functional
import server
import url

import re
import textwrap


QUOTE_PATTERN = re.compile(ur'[\"\u201c\u201e\u00ab]\s?(.+?)\s?[\"\u201c\u201d\u00bb]')
LINK_PATTERN = re.compile(r'https?://')


def dedent(string):
    return textwrap.dedent(string).replace('\n', '')

def extract_quotes(string):
    return re.findall(QUOTE_PATTERN, string)

def extract_links(string):
    words = string.split(' ')
    return [word for word in words if re.match(LINK_PATTERN, word)]
