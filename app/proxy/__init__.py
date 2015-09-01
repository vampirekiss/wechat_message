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
    def __init__(self, message_proxy_worker, message_parser):
        self.message_proxy_worker = message_proxy_worker
        self.parser = message_parser

    @coroutine
    def proxy_message(self, message_xml):
        message = self.parser.parse(message_xml)

        if message is not None:
            self.message_proxy_worker.proxy_message(message)
            return

        self.get_logger().error(
            "{} parse message xml failed\n{}".format(type(self.parser), message_xml)
        )