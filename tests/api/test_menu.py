# -*- coding: utf-8 -*-

from tests import AsyncHTTPTestCase
from app.application import Application
from app.api.menu import MenuHandler
from app.wechat.token import AccessToken


class MenuHandlerTestCase(AsyncHTTPTestCase):
    def setUp(self):
        self.mock_client = self.mock_coroutine_object('app.wechat.client.WechatClient')
        self.mock_provider = self.mock_coroutine_object('app.wechat.token.WechatAccessTokenProvider')
        MenuHandler._caches['menu_changed'] = True
        super(MenuHandlerTestCase, self).setUp()

    def get_app(self):
        return Application(
            [
                (
                    r"/api/v1/menu", MenuHandler,
                    dict(
                        wechat_client=self.mock_client,
                        wechat_access_token_provider=self.mock_provider
                    )
                )
            ]
        )

    def test_get_menu(self):
        token = AccessToken('token', 7200)
        self.mock_provider.set_method_result('get_access_token', token)
        self.mock_client.set_method_result('get_menu', {
            'menu': {
                'button': 'myblabla'
            }
        })
        response = self.get('/api/v1/menu')
        self.assertEqual(200, response.code)
        self.assertIn('myblabla', response.body)

    def test_get_menu_without_token(self):
        self.mock_provider.set_method_result('get_access_token', None)
        response = self.get('/api/v1/menu')
        self.assertEqual(200, response.code)
        self.assertEqual('{"menu": {}}', response.body)

    def test_create_menu_with_bad_request(self):
        response = self.post('/api/v1/menu', body='xx')
        self.assertEqual(400, response.code)

    def test_create_menu(self):
        token = AccessToken('token', 7200)
        self.mock_provider.set_method_result('get_access_token', token)
        menu_json = '{"button": "zzzdada"}'
        menu_response = {"errcode": 0, "msg": "ok"}
        self.mock_client.set_method_result('create_menu', menu_response)
        response = self.post('/api/v1/menu', body=menu_json)
        self.assertEqual(200, response.code)
        self.assertIn('ok', response.body)