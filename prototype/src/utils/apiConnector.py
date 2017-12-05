# -*- coding: utf-8 -*-
import requests
import json

class ApiConnector(object):
    def __init__(self):
        self.key = '1fee829e65de920d6de211b001ccc757'
        self.language = 'en'
        self.request_type = 'POST'
        self.request_url = 'http://api.meaningcloud.com/parser-2.0'
        self.headers = {'content-type': 'application/x-www-form-urlencoded'}
        self.request_params = {'verbose': 'y', 'lang': self.language, 'key': self.key}

    def make_request(self, text):
        self.request_params['txt'] = text
        response = requests.request(self.request_type,
                                    self.request_url,
                                    data=self.request_params,
                                    headers=self.headers)
        return json.loads(response.text)
