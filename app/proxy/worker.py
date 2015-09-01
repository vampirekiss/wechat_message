# -*- coding: utf-8 -*-
from __future__ import absolute_import

from abc import ABCMeta, abstractmethod
from tornado.ioloop import PeriodicCallback
from tornado.locks import Lock
from tornado.gen import coroutine, Return
from tornado.httpclient import HTTPError
from . import LoggingTrait

import time
import socket


class ProxyTargetMessagePairStorage(LoggingTrait):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_all(self):
        pass

    @abstractmethod
    def save(self, proxy_target, message):
        pass

    @abstractmethod
    def remove(self, proxy_target, message):
        pass

    def _get_item_key(self, proxy_target, message):
        return '{}_{}'.format(proxy_target.id, message.id)


class MemoryProxyTargetMessagePairStorage(ProxyTargetMessagePairStorage):
    def __init__(self):
        self.priority_item_dict = {}
        self.key_priority_dict = {}

    def get_all(self):
        priorities = self.priority_item_dict.keys()
        if len(priorities) == 0:
            return []
        result = []
        for key in priorities:
            item = self.priority_item_dict.get(key)
            if item:
                result.append(item)
        return result

    def save(self, sender, message):
        key = self._get_item_key(sender, message)
        if key in self.key_priority_dict:
            return
        priority = len(self.priority_item_dict)
        self.key_priority_dict[key] = priority
        self.priority_item_dict[priority] = (sender, message)

    def remove(self, sender, message):
        key = self._get_item_key(sender, message)
        if key in self.key_priority_dict:
            priority = self.key_priority_dict[key]
            del self.key_priority_dict[key]
            if priority in self.priority_item_dict:
                del self.priority_item_dict[priority]


class WechatMessageProxyWorker(LoggingTrait):
    def __init__(self, io_loop, proxy_targets, retry=True, failed_message_storage=None, max_retries=3, retry_period=10):
        self.io_loop = io_loop
        self.proxy_targets = self._proxy_targets_to_dict(proxy_targets)
        self.retry = retry
        self.message_retry_dict = {}
        self.failed_message_storage = failed_message_storage or MemoryProxyTargetMessagePairStorage()
        self.max_retires = max_retries
        self.retry_period = retry_period

        self.message_send_lock = Lock()
        self.message_retry_lock = Lock()

        if self.retry:
            self._start_retry_proxy_message_loop()

    def _proxy_targets_to_dict(self, proxy_targets):
        result = {}
        for proxy_target in proxy_targets:
            result[proxy_target.id] = proxy_target
        return result

    def _should_retry_on_error(self, e):
        error_type = type(e)
        if error_type is HTTPError:
            return e.code >= 500
        if error_type is socket.error:
            return True

        return False

    @coroutine
    def _proxy_pass_message(self, message):
        for proxy_target in self.proxy_targets.values():
            yield self._proxy_pass_message_to_target(proxy_target, message)

    @coroutine
    def _proxy_pass_message_to_target(self, proxy_target, message):
        if self.retry:
            yield self._proxy_pass_message_with_retry(proxy_target, message)
        else:
            try:
                yield proxy_target.proxy_pass(message)
            except:
                self.get_logger().exception("send message {} failed from {}".format(message, type(proxy_target)))

    @coroutine
    def _proxy_pass_message_with_retry(self, proxy_target, message):
        key = '{}{}'.format(proxy_target.id, message.id)
        if key not in self.message_retry_dict:
            self.message_retry_dict[key] = {
                'send_times': 0,
                'next_send_time': time.time() + self.retry_period,
                'key': key
            }

        message_retry_info = self.message_retry_dict[key]

        if message_retry_info['send_times'] == 0:
            allow_to_send = True
        else:
            allow_to_send = message_retry_info['send_times'] <= self.max_retires and \
                message_retry_info['next_send_time'] <= time.time()

        is_success = False

        if allow_to_send:
            try:
                yield proxy_target.proxy_pass(message)
                is_success = True
                del self.message_retry_dict[key]
            except Exception, e:
                if self._should_retry_on_error(e):
                    message_retry_info['next_send_time'] = time.time() + self.retry_period
                    self.failed_message_storage.save(proxy_target, message)
                else:
                    if key in self.message_retry_dict:
                        del self.message_retry_dict[key]
                self.get_logger().exception("proxy pass message {} failed from {}".format(message, type(proxy_target)))
            finally:
                message_retry_info['send_times'] += 1
        else:
            if message_retry_info['send_times'] > self.max_retires:
                self.get_logger().error("retry proxy pass message {} failed from {}".format(message, type(proxy_target)))
                if key in self.message_retry_dict:
                    del self.message_retry_dict[key]
                self.failed_message_storage.remove(proxy_target, message)

        raise Return(is_success)

    @coroutine
    def proxy_message(self, message):
        with (yield self.message_send_lock.acquire()):
            yield self._proxy_pass_message(message)

    @coroutine
    def _retry_proxy_message_task(self):
        items = self.failed_message_storage.get_all()
        for item in items:
            proxy_target, message = item
            is_success = yield self._proxy_pass_message_with_retry(proxy_target, message)
            if is_success:
                self.failed_message_storage.remove(proxy_target, message)

    def _start_retry_proxy_message_loop(self):
        callback_time = min(self.retry_period * 1000, 1000)
        PeriodicCallback(self._retry_proxy_message_task, callback_time, self.io_loop).start()
