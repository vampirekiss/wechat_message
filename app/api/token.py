# -*- coding: utf-8 -*-
from __future__ import absolute_import

from tornado.gen import coroutine
from app.api import TokenHolderHandler


class TokenHandler(TokenHolderHandler):

    def initialize(self, wechat_access_token_provider, token_request_validator):
        super(TokenHandler, self).initialize(wechat_access_token_provider)
        self.token_request_validator = token_request_validator

    @coroutine
    def get(self):
        if self.token_request_validator is not None:
            if not self.token_request_validator.is_valid(self):
                self._output_error_response(400, 'bad token request')
                return

        access_token = yield self._get_access_token()

        if access_token is None:
            return

        token_response = {
            'access_token': access_token.token,
            'expires_in': access_token.expires_in
        }

        self.write(token_response)

