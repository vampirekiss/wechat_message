# -*- coding: utf-8 -*-
from __future__ import absolute_import

from tornado.gen import coroutine
from app.api import BaseHandler


class MessageHandler(BaseHandler):
    def initialize(self, wechat_request_validator, wechat_message_proxy):
        self.wechat_request_validator = wechat_request_validator
        self.wechat_message_proxy = wechat_message_proxy

    def _is_valid_request(self):
        signature, timestamp, nonce = (
            self.get_query_argument('signature'),
            self.get_query_argument('timestamp'),
            self.get_query_argument('nonce'),
        )
        return self.wechat_request_validator.validate_signature(signature, timestamp, nonce)

    def get(self):
        if self._is_valid_request():
            self.write(self.get_query_argument('echostr'))
            return
        self._output_error_response(400, "bad signature")

    @coroutine
    def post(self):
        if self._is_valid_request():
            self.wechat_message_proxy.proxy_message(self.request.body)
            self.write('success')
        else:
            self._output_error_response(400, "bad signature")