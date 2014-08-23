import copy
import urllib
import facepy


def getdata(obj, key, default=None):
    if key in obj:
        return obj[key]['data']
    else:
        return default


class GraphAPI(facepy.GraphAPI):
    def __init__(self, *vargs, **kwargs):
        self.base = []
        super(GraphAPI, self).__init__(*vargs, **kwargs)

    def _resolve_endpoint(self, endpoint, options=None):
        if not isinstance(endpoint, list):
            endpoint = [endpoint]
        url = "/".join(self.base + endpoint)

        if options:
            qs = urllib.urlencode(options)
            return url + '?' + qs
        else:
            return url

    def partial(self, base):
        client = GraphAPI(self.oauth_token)
        client.base.append(self._normalize_endpoint(base))
        return client

    def all(self, endpoint, paramsets, method='GET', body=False, **options):
        """ A nicer interface for batch requests to the 
        same endpoint but with different parameters. """

        requests = []
        for params in paramsets:
            params = copy.copy(params)
            params.update(options)
            url = self._resolve_endpoint(endpoint, params)
            request = {
                'method': method, 
                'relative_url': url, 
                }

            if body:
                request['body'] = body

            requests.append(request)


        return self.batch(requests)

    def get(self, relative_endpoint, *vargs, **kwargs):
        """ An endpoint can be specified as a string
         or as a list of path segments. """

        endpoint = self._resolve_endpoint(relative_endpoint)
        return super(GraphAPI, self).get(endpoint, *vargs, **kwargs)
