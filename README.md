`facebook-insights` is a command-line utility that makes it easier to interact with Insights data in the Facebook Graph API. Python users can also directly access the API wrapper that the CLI is built on.

* **Authentication.** OAuth2 is a bit of a pain and we've made it easier.
* **Querying.** Query page and post insights with simple command-line parameters or through a pythonic interface.
* **Reporting.** Outputs simple timeseries of the data rather than verbose API responses.
* **Portability.** JSON output means you can analyze the data in any language from R to Julia to Ruby to Java.

**Development status:** the Python interface to `facebook-insights` is close to stable, but some things might change and others still need polish. The command-line interface is still very much a work in progress and you probably shouldn't try to use it yet.

## Authentication

You cannot use the Facebook Graph API with your Facebook username and password. Instead, you must authenticate through oAuth, first getting a user access token and then using that token to find the access tokens to the Facebook Pages for which you are an admin or for which you otherwise have permission to view the insights data.

### Short-term

Short term access (a couple of hours) is most easily gained through the [Graph API Explorer](https://developers.facebook.com/tools/explorer).

1. Go to the [Graph API Explorer](https://developers.facebook.com/tools/explorer)
2. Click on `Get Access Token` near the top of the page
3. Navigate to the `me/accounts` endpoint by entering it and clicking submit
4. Find and copy the page access token or tokens from the resulting JSON

On the command line: 

```sh
# (suggested interface, not built yet)
# use a token on every request
insights posts \
    --token <your token here> \
    --since 2014-08-01 \
    --until 2014-08-10 \
    --metrics post_impressions
# use a saved token from a `~/.facebookinsights` 
# INI file instead
insights posts \
    --profile <name>
```

In Python: 

```python
import facebookinsights as fi
page = fi.authenticate(token='your page token goes here')
```

### Long-term

It is also possible to ask Facebook for page tokens that remain valid indefinitely unless revoked by the page owner.

1. Go to the [Facebook Developers](https://developers.facebook.com/) portal, and click on `Apps > Create a New App`
2. Fill out the requisite information
3. After being redirected to your app's settings page, grab the App ID and App Secret. Save them somewhere, e.g. as environment variables in your `~/.bashrc`
4. Go to advanced settings and specify that your app is a `Native or desktop app`

If you intend to make your app public at some point, there are various other steps to go through: whitelisting callback URLs, going through the Facebook app approval process and so on.

If on the other hand you just want to analyze your own Facebook Insights data, you'll probably never need to look at your app settings again.

#### On your desktop

On the command-line, get authorization and save the resulting page tokens:

```sh
# (suggested interface, not built yet)
# provide client_id and client_secret
insights auth <client_id> <client_secret>
# use a profile from a `~/.facebookinsights` 
# INI file instead
insights auth --profile <name>
```

In Python:
    
```python
import facebookinsights as fi
# this will launch a web browser to authenticate
pages = fi.authenticate(
    client_id='your client id', 
    client_secret='your client secret', 
    )
```

If no arguments to `authenticate` are specified, `facebook-insights` will look for environment variables named `FACEBOOK_INSIGHTS_CLIENT_ID` and `FACEBOOK_INSIGHTS_CLIENT_SECRET` which correspond to the App ID and App Secret you got from your app's settings page earlier.

```python
import facebookinsights as fi
# this will launch a web browser to authenticate
pages = fi.authenticate()
```

`pages` will be a list of `Page` objects. You can access a page's token with `page.token`, which means you can make save those tokens for later use. This is especially important for analyses and other code that runs unattended, as getting new tokens through an oAuth authorization process always requires user interaction.

Here's an example that uses your system's keychain to store credentials: 

```python
import keyring
import json
import facebookinsights as fi

token = keyring.get_password('facebook-insights', 'test')
if token:
    page = fi.authenticate(token=token)
else:
    page = fi.authenticate()[0]
    keyring.set_password('facebook-insights', 'test', page.token)
```

#### In a web app

An example of how to integrate Facebook oAuth authorization in a Flask web app is provided in `examples/server.py`. The process is very similar for Django and other Python web frameworks: 

* One route that redirects to Facebook
* Another route that receives the authorization code from Facebook and exchanges it for a user token and subsequently for page tokens
