# encoding: utf-8

import os
from rauth import OAuth2Service
import utils
from utils.api import GraphAPI
import urlparse
import webbrowser

"""
To get a longer-lived page access token, 
exchange the User access token for a long-lived one, 
as above, and then request the Page token. The resulting 
page access token will not have any expiry time.
"""

PORT = 5000
REDIRECT_URI = 'http://localhost:{}/'.format(PORT)

def get_short_token(client_id, client_secret):
    facebook = OAuth2Service(
        client_id=client_id, 
        client_secret=client_secret, 
        authorize_url='https://graph.facebook.com/oauth/authorize',
        access_token_url='https://graph.facebook.com/oauth/access_token',
        base_url='https://graph.facebook.com/'
        )
    authorize_url = facebook.get_authorize_url(
        scope='manage_pages,read_insights',
        response_type='code',
        redirect_uri=REDIRECT_URI, 
        )
    webbrowser.open(authorize_url)
    qs = utils.server.single_serve(
        message='Authentication flow completed. You may close the browser tab.', 
        port=PORT, 
        )
    return facebook.get_access_token(data={
        'code': qs['code'],
        'grant_type': 'authorization_code', 
        'redirect_uri': REDIRECT_URI, 
        })

def get_long_token(client_id, client_secret, short_token):
    graph = GraphAPI()
    data = graph.get('oauth/access_token',   
        grant_type='fb_exchange_token', 
        client_id=client_id, 
        client_secret=client_secret, 
        fb_exchange_token=short_token
        )
    token = dict(urlparse.parse_qsl(data))
    return token['access_token']

def get_page_tokens(long_token):
    graph = GraphAPI(long_token)
    accounts = graph.get('me/accounts')['data']
    return [account['access_token'] for account in accounts]

def authorize(client_id, client_secret):
    short_token = get_short_token(client_id, client_secret)
    long_token = get_long_token(client_id, client_secret, short_token)
    tokens = get_page_tokens(long_token)
    return tokens
