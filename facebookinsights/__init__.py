# encoding: utf-8

import os
import oauth
import query

def authenticate(client_id=None, client_secret=None, tokens=[], token=None):
    if not client_id:
        client_id = os.environ.get('FACEBOOK_INSIGHTS_CLIENT_ID')
    if not client_secret:
        client_secret = os.environ.get('FACEBOOK_INSIGHTS_CLIENT_SECRET')
    if token:
        tokens = [token]

    if not (client_id and client_secret) or tokens:
        raise KeyError("""Authentication requires either one or more tokens, 
            or a client_id and client_secret passed to this function or available 
            in the environment as FACEBOOK_INSIGHTS_CLIENT_ID and 
            FACEBOOK_INSIGHTS_CLIENT_SECRET.""")

    graphs = oauth.ask_and_authenticate(client_id, client_secret, tokens)
    accounts = [query.Page(graph) for graph in graphs]
    return accounts
