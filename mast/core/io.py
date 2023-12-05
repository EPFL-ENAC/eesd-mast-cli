import requests
import json

class APIConnector:

    def __init__(self, api_url, api_key):
        self.api_url = api_url
        self.api_key = api_key

    def get(self, endpoint, params=None):
        return self._request('GET', endpoint, params=params)

    def post(self, endpoint, data=None):
        return self._request('POST', endpoint, data=data)

    def put(self, endpoint, data=None):
        return self._request('PUT', endpoint, data=data)

    def delete(self, endpoint, params=None):
        return self._request('DELETE', endpoint, params=params)

    def _request(self, method, endpoint, params=None, data=None):
        url = self.api_url + endpoint
        if params is None:
            params = {}
        if data is None:
            data = {}
        headers = {
            'Content-Type': 'application/json',
        }
        if self.api_key:
            headers['X-Api-Key'] = self.api_key
        response = requests.request(method, url, headers=headers, params=params, data=json.dumps(data))
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(response.text)