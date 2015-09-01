# -*- coding: utf-8 -*-
from __future__ import absolute_import

from abc import ABCMeta, abstractmethod
from tornado.gen import coroutine, Return
from tornado.httpclient import AsyncHTTPClient

import time
import string
import random
import hashlib
import urllib
import json


class AccessToken(object):
    def __init__(self, token, expires_in=None, expires_at=None):
        self.token = token
        self.spawn_time = int(time.time())

        if expires_in is None and expires_at is None:
            raise ValueError("expires_in or expires_at required any one")
        self.expires_at = expires_at or (self.spawn_time + expires_in)

    @property
    def expires_in(self):
        return int(self.expires_at - time.time())


class AccessTokenProvider(object):
    __metaclass__ = ABCMeta

    _cached_token_info = {
        'access_token': None
    }

    def __init__(self):
        self._cached_token_info = AccessTokenProvider._cached_token_info

    def _token_is_expired(self):
        access_token = self._cached_token_info.get('access_token')
        if access_token is None:
            return True
        return access_token.expires_at <= time.time()

    @coroutine
    def get_access_token(self):
        if not self._token_is_expired():
            access_token = self._cached_token_info.get('access_token')
        else:
            access_token = yield self._get_access_token()
            self._cached_token_info['access_token'] = access_token

        raise Return(access_token)

    @abstractmethod
    def _get_access_token(self):
        pass


class WechatAccessTokenProvider(AccessTokenProvider):
    def __init__(self, wechat_client):
        super(WechatAccessTokenProvider, self).__init__()
        self.wechat_client = wechat_client

    @coroutine
    def _get_access_token(self):
        response = yield self.wechat_client.get_access_token()
        if response.get('errcode') is not None:
            raise Return(None)
        token, expires_in = (response.get('access_token'), response.get('expires_in'))
        raise Return(AccessToken(token, expires_in))


class MissFreshAccessTokenProvider(AccessTokenProvider):
    def __init__(self, token, api_url, http_client=None):
        super(MissFreshAccessTokenProvider, self).__init__()
        self.token = token
        self.api_url = api_url
        self.http_client = http_client or AsyncHTTPClient()

    @coroutine
    def _get_access_token(self):
        url = self._build_request_url()
        response = yield self.http_client.fetch(url)
        document = json.loads(response.body)
        token = document.get('access_token')
        if token is None:
            access_token = None
        else:
            access_token = AccessToken(token, expires_at=document.get('expires_in'))
        raise Return(access_token)

    def _build_request_url(self):
        nonce = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
        timestamp = int(time.time())
        md5 = hashlib.md5()
        md5.update('{}{}{}'.format(nonce, timestamp, self.token))
        signature = str(md5.hexdigest()).upper()
        params = {
            'nonce': nonce,
            'timestamp': timestamp,
            'signature': signature
        }
        return '{}/interface/get-wx-token?{}'.format(self.api_url, urllib.urlencode(params))