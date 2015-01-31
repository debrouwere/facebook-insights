# encoding: utf-8

import os
from . import oauth
from . import graph
from . import utils
# import commands


def authenticate(client_id=None, client_secret=None, tokens=[], token=None):
    if not client_id:
        client_id = os.environ.get('FACEBOOK_INSIGHTS_CLIENT_ID')
    if not client_secret:
        client_secret = os.environ.get('FACEBOOK_INSIGHTS_CLIENT_SECRET')

    secrets = client_id and client_secret
    credentials = token or tokens
    if secrets:
        tokens = oauth.authorize(client_id, client_secret)
    elif credentials:
        pass
    else:
        raise KeyError(utils.dedent("""
            Authentication requires either one or more tokens, 
            or a client_id and client_secret passed to this 
            function or available in the environment as 
            FACEBOOK_INSIGHTS_CLIENT_ID and 
            FACEBOOK_INSIGHTS_CLIENT_SECRET.
            """))
    if token:
        return graph.Page(token)
    else:
        return [graph.Page(token) for token in tokens]
