# -*- coding: utf-8 -*-

from tests import AsyncHTTPTestCase
from app.application import Application
from app.api.token import TokenHandler
from app.proxy.targets import live800
from app.wechat.token import AccessToken


class TokenHandlerTestCase(AsyncHTTPTestCase):

    def setUp(self):
        self.mock_provider = self.mock_coroutine_object('app.wechat.token.WechatAccessTokenProvider')
        super(TokenHandlerTestCase, self).setUp()

    def get_app(self):
        return Application(
            [
                (
                    r"/api/v1/getAccessToken", TokenHandler,
                    dict(
                        wechat_access_token_provider=self.mock_provider,
                        token_request_validator=live800.TokenRequestValidator('token')
                    )
                )
            ]
        )

    def test_get_token_with_error_signature(self):
        response = self.get('/api/v1/getAccessToken?bla')
        self.assertEqual(response.code, 400)
        self.assertIn('bad token request', response.body)

    def test_get_token(self):
        token = AccessToken('random_access_token', 7200)
        self.mock_provider.set_method_result('get_access_token', token)
        response = self.get('/api/v1/getAccessToken?nonce=1&timestamp=2&signature=8FF88EB850E4C03430E1712A4C2D2479')
        self.assertEqual(response.code, 200)
        self.assertIn('random_access_token', response.body)
