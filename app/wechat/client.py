# -*- coding: utf-8 -*-
from __future__ import absolute_import

from tornado.httpclient import AsyncHTTPClient
from tornado.gen import coroutine, Return

import urllib
import json


class WechatClient(object):
    def __init__(self, api_url, app_id, secret, http_client=None):
        self.api_url = api_url
        self.app_id = app_id
        self.secret = secret
        self.http_client = http_client or AsyncHTTPClient()

    @coroutine
    def _post_json(self, access_token, json_str, path):
        params = {
            'access_token': access_token
        }
        url = '{}{}?{}'.format(self.api_url, path, urllib.urlencode(params))
        response = yield self.http_client.fetch(
            url, method='POST',
            headers={"Content-Type": "application/json"}, body=json_str
        )
        raise Return(json.loads(response.body))

    @coroutine
    def get_access_token(self, grant_type='client_credential'):
        if grant_type != 'client_credential':
            raise NotImplementedError
        params = {
            'grant_type': grant_type,
            'appid': self.app_id,
            'secret': self.secret
        }
        url = '{}/token?{}'.format(self.api_url, urllib.urlencode(params))
        response = yield self.http_client.fetch(url)
        raise Return(json.loads(response.body))

    @coroutine
    def get_menu(self, access_token):
        params = {
            'access_token': access_token
        }
        url = '{}/menu/get?{}'.format(self.api_url, urllib.urlencode(params))
        response = yield self.http_client.fetch(url)
        raise Return(json.loads(response.body))

    @coroutine
    def create_menu(self, access_token, menu_json_str):
        result = yield self._post_json(access_token, menu_json_str, '/menu/create')
        raise Return(result)

    @coroutine
    def send_custom_message(self, access_token, message):
        message_json = json.dumps(message, ensure_ascii=False)
        result = yield self._post_json(access_token, message_json, '/message/custom/send')
        raise Return(result)

