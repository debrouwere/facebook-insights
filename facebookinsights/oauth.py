# encoding: utf-8

import os
import rauth
import webbrowser
from . import utils
from .utils.api import GraphAPI

"""
To get a longer-lived page access token, 
exchange the User access token for a long-lived one, 
as above, and then request the Page token. The resulting 
page access token will not have any expiry time.
"""


PORT = 5000
REDIRECT_URI = 'http://localhost:{}/'.format(PORT)


class OAuth2Service(rauth.OAuth2Service):
    def __init__(self, *vargs, **kwargs):
        options = dict(
            authorize_url='https://graph.facebook.com/oauth/authorize', 
            access_token_url='https://graph.facebook.com/oauth/access_token', 
            base_url='https://graph.facebook.com/', 
            )
        options.update(**kwargs)
        self.redirect_uri = options.get('redirect_uri')
        if 'redirect_uri' in options:
            del options['redirect_uri']
        super(OAuth2Service, self).__init__(*vargs, **options)

    def get_authorize_url(self, *vargs, **kwargs):
        options = dict(
            scope='manage_pages,read_insights',
            response_type='code',            
            redirect_uri=self.redirect_uri, 
            )
        options.update(**kwargs)
        return super(OAuth2Service, self).get_authorize_url(*vargs, **options)

    def get_access_token(self, code, *vargs, **kwargs):
        long_term = kwargs.get('long_term', False)
        if 'long_term' in kwargs:
            del kwargs['long_term']

        data = dict(
            code=code,
            grant_type='authorization_code', 
            redirect_uri=self.redirect_uri, 
            )
        data.update(kwargs.get('data', {}))
        kwargs['data'] = data
        token = super(OAuth2Service, self).get_access_token(
            *vargs, **kwargs)

        if long_term:
            token = self.get_long_term_token(token)

        return token

    def get_long_term_token(self, short_token):
        graph = GraphAPI()
        data = graph.get('oauth/access_token',   
            grant_type='fb_exchange_token', 
            client_id=self.client_id, 
            client_secret=self.client_secret, 
            fb_exchange_token=short_token, 
            )
        token = dict(utils.url.parse.parse_qsl(data))
        return token['access_token']

    def get_page_tokens(self, long_token):
        graph = GraphAPI(long_token)
        accounts = graph.get('me/accounts')['data']
        return [account['access_token'] for account in accounts]


def authorize_user(facebook, long_term=False):
    authorize_url = facebook.get_authorize_url()
    webbrowser.open(authorize_url)
    qs = utils.server.single_serve(
        message='Authentication flow completed. You may close the browser tab.', 
        port=PORT, 
        )
    return facebook.get_access_token(qs['code'], long_term=long_term)

def authorize_pages(facebook, user_token):
    return facebook.get_page_tokens(user_token)

def authorize(client_id, client_secret):
    facebook = OAuth2Service(
        client_id=client_id, 
        client_secret=client_secret,
        redirect_uri=REDIRECT_URI, 
        )
    user_token = authorize_user(facebook, long_term=True)
    page_tokens = authorize_pages(facebook, user_token)
    return page_tokens
