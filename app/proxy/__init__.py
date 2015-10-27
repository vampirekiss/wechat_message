# -*- coding: utf-8 -*-
from __future__ import absolute_import

from tornado.gen import coroutine
from abc import ABCMeta, abstractmethod
from cached_property import cached_property

import logging
import uuid


class LoggingTrait(object):
    def get_logger(self):
        return logging.getLogger("tornado.application")


class WechatMessageProxyTarget(LoggingTrait):
    __metaclass__ = ABCMeta

    @cached_property
    def id(self):
        return str(uuid.uuid4()).upper()

    @abstractmethod
    def proxy_pass(self, message):
        pass


class WechatMessageProxy(LoggingTrait):
    def __init__(self, token_provider, message_parser, message_proxy_worker, message_event_handlers):
        self.token_provider = token_provider
        self.parser = message_parser
        self.message_proxy_worker = message_proxy_worker
        self.message_event_handlers = message_event_handlers

    @coroutine
    def proxy_message(self, message_xml):
        message = self.parser.parse(message_xml)

        if message is None:
            return

        if message.is_event():
            access_token = yield self.token_provider.get_access_token()
            if access_token is not None:
                for handler in self.message_event_handlers:
                    yield handler.handle(access_token.token, message)
        else:
            yield self.message_proxy_worker.proxy_message(message)

        # 忽略不能解析的消息
        # self.get_logger().error(
        #     "{} parse message xml failed\n{}".format(type(self.parser), message_xml)
        # )
