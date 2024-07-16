import requests
import json
import sys

class APIConnector:

    def __init__(self, api_url, api_key):
        self.api_url = api_url
        self.api_key = api_key

    def get(self, endpoint, params=None):
        return self._request("GET", endpoint, params=params)

    def post(self, endpoint, data=None):
        return self._request("POST", endpoint, data=data)
    
    def upload(self, endpoint, files):
        url = self._url(endpoint)
        headers = self._headers()
        del headers["Content-Type"]
        response = requests.post(url, headers=headers, files=files)
        if response.status_code == 200:
            return response.json()
        else:
            self._handleError(response)
    
    def download(self, endpoint: str, path: str):
        url = self._url(endpoint)
        headers = self._headers()
        response = requests.request("GET", url, headers=headers)
        if response.status_code == 200:
            if response.headers["content-type"] == "application/json":
                return response.json()
            else:
                with open(path, 'wb') as file:
                    file.write(response.content)
        else:
            self._handleError(response)
        
    def put(self, endpoint, data=None):
        return self._request("PUT", endpoint, data=data)

    def delete(self, endpoint, params=None):
        return self._request("DELETE", endpoint, params=params)

    def _url(self, endpoint):
        return self.api_url + endpoint

    def _headers(self):
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.api_key:
            headers["X-Api-Key"] = self.api_key
        return headers

    def _request(self, method, endpoint, params=None, data=None):
        url = self._url(endpoint)
        headers = self._headers()
        if params is None:
            params = {}
        if data is None:
            data = {}
        response = requests.request(method, url, headers=headers, params=params, data=json.dumps(data))
        if response.status_code == 200:
            if response.headers["content-type"] == "application/json":
                return response.json()
            else:
                return sys.stdout.write(response.text)
        else:
            self._handleError(response)
    
    def _handleError(self, response):
        if response.headers["content-type"] == "application/json":
            message = response.json()
            if "detail" in message:
                raise Exception(message["detail"])
            else:
                raise Exception(message)
        else:
            raise Exception(response.text)