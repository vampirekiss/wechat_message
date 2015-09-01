# -*- coding: utf-8 -*-
from __future__ import absolute_import

from tornado.httpclient import AsyncHTTPClient
from tornado.gen import coroutine
from app.proxy import WechatMessageProxyTarget

import hashlib
import random
import time


class _Live800TokenHolder(object):
    def __init__(self, token):
        self.token = token


class ProxyTarget(_Live800TokenHolder, WechatMessageProxyTarget):
    def __init__(self, token, api_url, http_client=None):
        super(ProxyTarget, self).__init__(token)
        self.api_url = api_url
        self.http_client = http_client or AsyncHTTPClient()

    @coroutine
    def proxy_pass(self, message):
        nonce = str(random.randint(10000, 99999))
        timestamp = str(int(time.time()))
        params = [self.token, nonce, timestamp]
        params.sort()
        signature = str(hashlib.sha1(''.join(params)).hexdigest())
        echostr = str(hashlib.md5(str(time.time())).hexdigest())
        url = '{}?timestamp={}&nonce={}&echostr={}&signature={}'.format(
            self.api_url, timestamp, nonce, echostr, signature
        )
        body = message.xml
        headers = {'Content-Type': 'application/xml', 'Content-Length': len(body)}
        yield self.http_client.fetch(url, method='POST', body=body, headers=headers)


class TokenRequestValidator(_Live800TokenHolder):
    def is_valid(self, request_handler):
        nonce, timestamp, signature = (
            request_handler.get_query_argument('nonce', ''),
            request_handler.get_query_argument('timestamp', ''),
            request_handler.get_query_argument('signature', ''),
        )
        valid_signature = self._make_signature(nonce, timestamp)
        return valid_signature == signature

    def _make_signature(self, nonce, timestamp):
        nonce = nonce.encode('utf-8')
        timestamp = timestamp.encode('utf-8')
        token = unicode(self.token).encode('utf-8')
        md5 = hashlib.md5()
        md5.update(u'{}{}{}'.format(nonce, timestamp, token))
        return str(md5.hexdigest()).upper()