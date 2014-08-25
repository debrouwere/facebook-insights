# encoding: utf-8

import keyring
import json
import facebookinsights as fi

token = keyring.get_password('facebook-insights', 'test')
if token:
    page = fi.authenticate(token=token)
else:
    page = fi.authenticate()[0]
    keyring.set_password('facebook-insights', 'test', page.token)

if __name__ == '__main__':
    """
    one_day = page.posts.range('2014-08-19', '2014-08-20')

    for post in one_day:
        print post.created_time, post.link #post.resolve_link(clean=True)

    for post in page.posts.latest(5):
        print post.link
    """

    print page.insights.daily('page_stories').get()
    print page.insights.daily(['page_stories', 'page_storytellers']).get()

    post = page.posts.latest(10)[-1]
    metrics = ['post_impressions', 'post_consumptions']
    query = post.insights.lifetime(metrics)
    print query
    insights = query.get()
    print insights
    print json.dumps(query.serialize(), indent=4)


"""
from facepy import GraphAPI

graph = GraphAPI(access_token)

import facebookinsights as fi

# similar deal with `ask_and_authenticate` for oAuth flow
page = fi.authenticate()

page.posts.limit(100)
page.posts.range('2013-01-01', '2013-05-01')
page.posts.find(url='yadda')

post.insights.daily(since=...)

post = page.posts.last()
# get (generic), daily, weekly, monthly, lifetime
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