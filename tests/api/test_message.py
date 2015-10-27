# -*- coding: utf-8 -*-

from tests import AsyncHTTPTestCase
from app.application import Application
from app.api.message import MessageHandler
from app.proxy import WechatMessageProxy
from app.proxy.event import WechatReplyTextMessageHandler
from app.wechat.message import WechatMessageParser, WechatMessageRequestValidator, WechatEventSetting
from app.wechat.token import AccessToken


class MessageHandlerTestCase(AsyncHTTPTestCase):

    def setUp(self):
        self.wechat_message_worker = self.mock_coroutine_object(
            "app.proxy.worker.WechatMessageProxyWorker"
        )
        self.token_provider = self.mock_coroutine_object(
            "app.wechat.token.AccessTokenProvider"
        )
        self.wechat_client = self.mock_coroutine_object(
            "app.wechat.client.WechatClient"
        )
        self.message_event_handlers = [
            WechatReplyTextMessageHandler(
                self.wechat_client,
                WechatEventSetting(
                    setting=
                    {
                        WechatEventSetting.Subscribe_Reply_Text: "subscribe"
                    }
                )
            )
        ]
        self.wechat_message_worker.mock_method('proxy_message', self._proxy_message)
        self.wechat_message_proxy = WechatMessageProxy(
            self.token_provider,
            WechatMessageParser(),
            self.wechat_message_worker,
            self.message_event_handlers
        )
        self.access_token = AccessToken('abcd', 7200)
        self.token_provider.set_method_result('get_access_token', self.access_token)
        self.wechat_request_validator = WechatMessageRequestValidator("token")
        self.proxy_passed_message = None
        self.url = "/api/v1/message?signature=59d7df0c0961b050088fe2cc833340663d12bd03" \
                   "&timestamp=1441077547&nonce=1917417690"
        super(MessageHandlerTestCase, self).setUp()

    def get_app(self):
        return Application(
            [
                (
                    r"/api/v1/message", MessageHandler,
                    dict(
                        wechat_request_validator=self.wechat_request_validator,
                        wechat_message_proxy=self.wechat_message_proxy
                    )
                )
            ]
        )

    def _proxy_message(self, message):
        self.proxy_passed_message = message

    def test_get(self):
        response = self.get("/api/v1/message")
        self.assertEqual(400, response.code)
        url = "{}&echostr=123456".format(self.url)
        response = self.get(url)
        self.assertEqual(200, response.code)
        self.assertEqual('123456', response.body)

    def test_post_without_signature(self):
        response = self.post("/api/v1/message", body='xx')
        self.assertEqual(400, response.code)

    def test_post_bad_message(self):
        response = self.post(self.url, body='xx')
        self.assertEqual(200, response.code)
        self.assertIsNone(self.proxy_passed_message)

    def test_post_message(self):
        xml = """
            <xml>
                 <ToUserName><![CDATA[toUser]]></ToUserName>
                 <FromUserName><![CDATA[fromUser]]></FromUserName>
                 <CreateTime>1348831860</CreateTime>
                 <MsgType><![CDATA[text]]></MsgType>
                 <Content><![CDATA[this is a test]]></Content>
                 <MsgId>1234567890123456</MsgId>
            </xml>
        """
        response = self.post(self.url, body=xml)
        self.assertEqual(200, response.code)
        self.assertIsNotNone(self.proxy_passed_message)
        self.assertEqual("1234567890123456", self.proxy_passed_message.id)

    def _post_event(self, event_type):
        xml = """
            <xml>
                <ToUserName><![CDATA[toUser]]></ToUserName>
                <FromUserName><![CDATA[from_user_name]]></FromUserName>
                <CreateTime>123456789</CreateTime>
                <MsgType><![CDATA[event]]></MsgType>
                <Event><![CDATA[%s]]></Event>
            </xml>
        """ % event_type

        ctx = {}

        def _send_custom_message(token, message):
            ctx['access_token'] = token
            ctx['reply_message'] = message

        self.wechat_client.mock_method('send_custom_message', _send_custom_message)

        response = self.post(self.url, body=xml)
        return response, ctx

    def test_post_subscribe_event(self):
        response, ctx = self._post_event("subscribe")
        self.assertEqual(200, response.code)
        self.assertTrue('access_token' in ctx)
        self.assertTrue('reply_message' in ctx)
        self.assertEqual(ctx['access_token'], self.access_token.token)
        self.assertEqual(ctx['reply_message']['touser'], 'from_user_name')
        self.assertEqual(ctx['reply_message']['text']['content'], 'subscribe')