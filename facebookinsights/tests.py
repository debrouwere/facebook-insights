# encoding: utf-8

import facebookinsights as fi

pages = fi.authenticate()
print pages

"""
from facepy import GraphAPI

graph = GraphAPI(access_token)

import facebookinsights as fi

# similar deal with `ask_and_authenticate` for oAuth flow
page = fi.authenticate()

page.posts.limit(100)
page.posts.range('2013-01-01', '2013-05-01')
page.posts.find(url='yadda')

post = page.posts.last()
# get (generic), hourly, daily, weekly, monthly, lifetime
# (monthly always means 28 days)
post.daily('likes')
post.monthly(['likes', 'comments'])
post.daily() # all applicable metrics

# manual works too
page = fi.Page('id')
post = fi.Post('id')

# metrics are classless, rows are named tuples
# column plucking is possible
post.daily()[0].likes
post.daily()['likes'][0]
post.daily('likes')[0]

# pass on certain values to facepy
post.daily(retry=3)
"""