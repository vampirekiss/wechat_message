# -*- coding: utf-8 -*-
from __future__ import absolute_import

from tornado.gen import coroutine
from app.api import TokenHolderHandler, BasicAuthHandlerMixin

import json


class MenuHandler(TokenHolderHandler, BasicAuthHandlerMixin):
    _caches = {
        'menu_changed': False,
        'menu': None
    }

    def initialize(self, wechat_client, wechat_access_token_provider, **kwargs):
        super(MenuHandler, self).initialize(wechat_access_token_provider, **kwargs)
        self.wechat_client = wechat_client
        self._caches = MenuHandler._caches

    @coroutine
    def get(self):
        if self._caches['menu_changed'] is False and self._caches['menu'] is not None:
            self._output_menu_response(self._caches['menu'])
            return

        access_token = yield self._get_access_token(output_error=False)

        if access_token is None:
            self._output_menu_response({})
            return

        menu = yield self.wechat_client.get_menu(access_token.token)

        error_code = menu.get('errcode')

        if error_code is not None and error_code != 46003:
            self._output_menu_response([])
            return

        menu = {} if error_code == 46003 else menu.get('menu')

        self._caches['menu_changed'] = False
        self._caches['menu'] = menu

        self._output_menu_response(self._caches['menu'])

    def _output_menu_response(self, menu):
        response = {
            'menu': menu
        }
        self.write(response)

    @coroutine
    def post(self):
        json_str = self.request.body
        try:
            menu = json.loads(json_str)
        except:
            self._output_error_response(400, 'bad request')
            return

        access_token = yield self._get_access_token()
        if access_token is None:
            return

        response = yield self.wechat_client.create_menu(access_token.token, json_str)
        if response.get('errcode', 0) == 0:
            self._caches['menu'] = menu

        self.write(response)