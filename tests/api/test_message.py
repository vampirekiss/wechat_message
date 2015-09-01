# -*- coding: utf-8 -*-

from tests import AsyncHTTPTestCase
from app.application import Application
from app.api.message import MessageHandler
from app.proxy import WechatMessageProxy
from app.wechat.message import WechatMessageParser, WechatMessageRequestValidator


class MessageHandlerTestCase(AsyncHTTPTestCase):

    def setUp(self):
        self.wechat_message_worker = self.mock_coroutine_object(
            "app.proxy.worker.WechatMessageProxyWorker"
        )
        self.wechat_message_worker.mock_method('proxy_message', self._proxy_message)
        self.wechat_message_proxy = WechatMessageProxy(
            self.wechat_message_worker, WechatMessageParser()
        )
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

