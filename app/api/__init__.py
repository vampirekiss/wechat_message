# -*- coding: utf-8 -*-
from __future__ import absolute_import

from tornado.web import RequestHandler, HTTPError
from tornado.gen import coroutine, Return
from tornado.httputil import responses

import logging


class BaseHandler(RequestHandler):
    def __init__(self, application, request, **kwargs):
        super(BaseHandler, self).__init__(application, request, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)

    def data_received(self, chunk):
        pass

    def write_error(self, status_code, **kwargs):
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write({
            'errcode': status_code,
            'errmsg': responses.get(status_code, 'internal error')
        })

    def _output_error_response(self, status_code, reason):
        self.write({
            'errcode': status_code,
            'errmsg': reason
        })
        self.set_status(status_code)


class ErrorHandler(BaseHandler):
    def initialize(self, status_code=404):
        self.set_status(status_code)

    def prepare(self):
        raise HTTPError(self._status_code)


class TokenHolderHandler(BaseHandler):
    def initialize(self, wechat_access_token_provider):
        self.token_provider = wechat_access_token_provider

    @coroutine
    def _get_access_token(self, output_error=True):
        access_token = yield self.token_provider.get_access_token()
        if access_token is None and output_error:
            self._output_error_response(500, 'can not get access token')
            return
        raise Return(access_token)
