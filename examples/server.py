import os
from flask import Flask, request, redirect, jsonify
import facebookinsights as fi

app = Flask(__name__)

PORT = 5000
CLIENT_ID = os.environ['FACEBOOK_INSIGHTS_CLIENT_ID']
CLIENT_SECRET = os.environ['FACEBOOK_INSIGHTS_CLIENT_SECRET']
REDIRECT_ROUTE = '/auth/facebook/callback'
REDIRECT_URI = 'http://localhost:{}'.format(PORT) + REDIRECT_ROUTE

facebook = fi.oauth.OAuth2Service(
    client_id=CLIENT_ID, 
    client_secret=CLIENT_SECRET, 
    redirect_uri=REDIRECT_URI, 
    )

@app.route('/auth/facebook')
def authorization():
    authorize_url = facebook.get_authorize_url()
    return redirect(authorize_url)

@app.route(REDIRECT_ROUTE)
def callback():
    user_token = facebook.get_access_token(
        request.args['code'], long_term=True)
    page_tokens = facebook.get_page_tokens(user_token)
    return jsonify(page_tokens=page_tokens)

app.run(port=PORT)