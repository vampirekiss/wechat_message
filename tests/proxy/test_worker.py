# -*- coding: utf-8 -*-

from tornado.testing import AsyncTestCase, gen_test
from tornado.gen import sleep

from app.proxy.worker import WechatMessageProxyWorker
from app.wechat.message import WechatMessage
from tests import TestCaseMixin

import os
import socket


os.environ['ASYNC_TEST_TIMEOUT'] = '600'


class WechatMessageProxyWorkerTestCase(AsyncTestCase, TestCaseMixin):
    def setUp(self):
        self.proxy_target = self.mock_coroutine_object("app.proxy.WechatMessageProxyTarget")
        self.proxy_passed_message = None
        self.proxy_passed_times_dict = {}
        super(WechatMessageProxyWorkerTestCase, self).setUp()

    def _proxy_pass(self, message):
        self.proxy_passed_message = message

    def _proxy_pass_with_retry(self, message):
        if message.id not in self.proxy_passed_times_dict:
            self.proxy_passed_times_dict[message.id] = 0
        else:
            self.proxy_passed_times_dict[message.id] += 1

        self.proxy_passed_message = message
        raise socket.error("proxy pass failed")

    def test_proxy_message_without_retry(self):
        self.assertIsNone(self.proxy_passed_message)

        self.proxy_target.mock_method("proxy_pass", self._proxy_pass)
        worker = WechatMessageProxyWorker(self.io_loop, [self.proxy_target], False)
        message = WechatMessage("<xml></xml>", "message_1")
        worker.proxy_message(message)

        self.assertIsNotNone(self.proxy_passed_message)
        self.assertEqual("message_1", self.proxy_passed_message.id)

    @gen_test
    def test_proxy_message_with_retry(self):
        self.assertIsNone(self.proxy_passed_message)

        self.proxy_target.mock_method("proxy_pass", self._proxy_pass_with_retry)
        worker = WechatMessageProxyWorker(self.io_loop, [self.proxy_target], retry_period=0.01)

        for i in range(1, 101):
            message = WechatMessage("<xml></xml>", "message_{}".format(i))
            yield worker.proxy_message(message)
            self.assertIsNotNone(self.proxy_passed_message)
            self.assertEqual("message_{}".format(i), self.proxy_passed_message.id)

        while len(worker.message_retry_dict) > 0:
            yield sleep(0.1)

        self.assertEqual(100, len(self.proxy_passed_times_dict))
        for times in self.proxy_passed_times_dict.values():
            self.assertEqual(3, times)