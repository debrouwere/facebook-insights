`facebook-insights` is a command-line utility that makes it easier to interact with [Insights metrics in the Facebook Graph API](https://developers.facebook.com/docs/graph-api/reference/v2.2/insights). Python users can also directly access the API wrapper that the CLI is built on.

* **Authentication.** OAuth2 is a bit of a pain and we've made it easier.
* **Querying.** Query page and post insights with simple command-line parameters or through a pythonic interface.
* **Reporting.** Outputs simple timeseries of the data rather than verbose API responses.
* **Portability.** JSON output means you can analyze the data in any language from R to Julia to Ruby to Java.

**Development status:** the Python interface to `facebook-insights` is close to stable, but some things might change and others still need polish. The command-line interface is still very much a work in progress and you probably shouldn't try to use it yet.

## Usage

#### Authentication

```python
import os
import facebookinsights as fi

# prompt for credentials on the command-line, 
# get access to one or more pages
pages = fi.authenticate()
# alternatively, pass an existing page token
page = fi.authenticate(token=os.environ['FACEBOOK_PAGE_TOKEN'])
```

Scroll down to find out more about authentication.

#### Page Posts

Facebook provides Insights data for the page as a whole (follower counts, impressions across all stories etc.), for all page posts taken together (likes for all page posts published last week etc.) and for individual posts (video plays for one particular post etc.)

```python
# return a range of page posts
latest = page.posts.latest(10).get()
today = page.posts.range(days=1).get()
quarter = page.posts.range(months=3).get()

# look for a particular post instead
page.posts.find(url='http://fusion.net/story/37894/narcotrafficking-for-dummies-check-out-these-pics-of-bizarre-drug-smuggling-fails/')
```

#### Reporting Periods

For many metrics, Facebook Insights includes historical data, so you can see e.g. how your page's fans have increased or decreased over time. However, for some page metrics and most post metrics, only lifetime metrics are available, which represent the current state of things.

```python
# for many metrics, historical data is available, with daily, weekly 
# and 4-weekly rollups, accessible through `daily`, `weekly` and 
# `monthly` methods
page.insights.daily(['page_impressions', 'page_fan_adds']).range(months=1).get()
# for other metrics, there's only a lifetime total
post.insights.lifetime('post_stories').get()
# for some, it's the other way around: no total, only the daily numbers
for country_data in page.insights.daily('page_places_checkins_by_country'):
    print country_data
```

Also note that some metrics are updated roughly every 15 minutes whereas others can lag behind up to a day. Metrics postfixed with an asterisk in the [Facebook Graph API documentation](https://developers.facebook.com/docs/graph-api/reference/v2.2/insights) indicate frequently updated metrics.

**Note:** currently, `facebook-insights` will not throw an error if you ask for a metric at an impossible granularity. Instead, Facebook will return data at the granularity (often lifetime) that it can provide.

#### Metrics

It is possible to ask for one or more metrics in particular.

```python
# results will be returned as a single scalar value
page.insights.lifetime('page_impressions').get()
# results will be returned as an array
page.insights.lifetime(['page_impressions', 'page_fan_adds']).get()
# default metrics subset
page.insights.lifetime().get()
```

If no metrics are specified, the Facebook Graph API will return a useful subset by default.

#### Query Results

```python
# metrics are classless, rows are named tuples
# column plucking is possible
post.lifetime()[0].page_fans
post.daily()['page_fans'][0]
post.daily('page_fans')[0]
```

#### Lower-level

`facebook-insights` is built on the [FacePy](https://github.com/jgorset/facepy) library, and you may pass certain low-level options to FacePy when executing queries:

```python
post.daily('page_fans_online_per_day', retry=3)
```

## Terminology

* **page**: a Facebook (fan) page
* **page post**: a post to a Facebook page
* **story**: a user interaction with a page, e.g. "Mike liked this page." or "Jeb shared this post with his friends."
* **story type**: the type of interaction a user has with a page, e.g. a checkin, a mention or a like.
* **storyteller**: a user who interacts with a page (e.g. by liking a page post)
* **impression**: a view of either the page or a page post
* **engaged user**: a user who clicked anywhere on a page or a page post
* **consumption**: a click on a page or a page post; an engaged user can show up as one or more consumptions
* **fan**: a user who has liked your page and will usually see it in their feed. Similar to a Twitter follower.
* **unique**: count no more than once per user
* **organic**: impressions or interactions not the result of promoting your post, as opposed to paid impressions and interactions
* **feedback**: positive feedback includes likes, shares and so on; negative feedback includes hiding, unliking and reporting spam.

Most of this terminology applies both at the page level and at the page post level. For example: 

* `page_impressions_unique` at the page level
* `page_posts_impressions_unique` for interactions with any page post
* `post_impressions_unique` about one particular post

You will find more detailed explanations of much of this terminology and a list of all story and feedback types in the [Facebook Graph API Insights documentation](https://developers.facebook.com/docs/graph-api/reference/v2.2/insights), which is excellent.

## Page and Post objects

Pending better documentation, to find out more about what properties and methods are available on `Page`, `Post`, `Picture` objects, please take a look at `facebookinsights/graph.py`.

To find out more detailed information about querying, look at `Selection`, `PageSelection` and `InsightsSelection` in `facebookinsights/graph.py`.

## Authentication in detail

You cannot use the Facebook Graph API with your Facebook username and password. Instead, you must authenticate through oAuth, first getting a user access token and then using that token to find the access tokens to the Facebook Pages for which you are an admin or for which you otherwise have permission to view the insights data.

### Short-term

Short term access (a couple of hours) is most easily gained through the [Graph API Explorer](https://developers.facebook.com/tools/explorer).

1. Go to the [Graph API Explorer](https://developers.facebook.com/tools/explorer)
2. Click on `Get Access Token` near the top of the page
3. Navigate to the `me/accounts` endpoint by entering it and clicking submit
4. Find and copy the page access token or tokens from the resulting JSON

On the command line: 

```sh
# WARNING: suggested interface, not built yet
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
5. Lower down on the advanced settings page, add `http://localhost:5000/` to the Valid OAuth redirect URIs.

If you intend to make your app public at some point, there are various other steps to go through: whitelisting callback URLs, going through the Facebook app approval process and so on.

If on the other hand you just want to analyze your own Facebook Insights data, you'll probably never need to look at your app settings again.

#### On your desktop

On the command-line, get authorization and save the resulting page tokens:

```sh
# WARNING: suggested interface, not built yet
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
