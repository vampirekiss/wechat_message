# -*- coding: utf-8 -*-

from tornado.testing import IOLoop, AsyncHTTPTestCase as BaseAsyncHTTPTestCase
from tornado.gen import coroutine, Return
from app.application import Application
from urllib import urlencode

import mock


class TestCaseMixin(object):
    def get_new_ioloop(self):
        return IOLoop.instance()

    def mock_coroutine_object(self, klass):
        return _CoroutineMockObject(klass)


class AsyncHTTPTestCase(BaseAsyncHTTPTestCase, TestCaseMixin):
    def get_app(self):
        return Application()

    def get(self, url, **kwargs):
        return self.fetch(url, **kwargs)

    def post(self, url, **kwargs):
        if 'body' in kwargs and isinstance(kwargs['body'], dict):
            kwargs['body'] = urlencode(kwargs['body'])
        return self.fetch(url, method='POST', **kwargs)


class _CoroutineMockObject(object):
    def __init__(self, klass):
        self.mock_object = mock.patch(klass).start()
        self.mocked_methods = {}

    def set_method_result(self, method, result):
        @coroutine
        def side_effect(*args, **kwargs):
            raise Return(result)
        self.mocked_methods[method] = True
        self.mock_object[method].side_effect = side_effect

    def mock_method(self, method, target):
        @coroutine
        def side_effect(*args, **kwargs):
            raise Return(target(*args, **kwargs))
        self.mocked_methods[method] = True
        self.mock_object[method].side_effect = side_effect

    def __getattr__(self, method):
        if method in self.mocked_methods:
            return self.mock_object[method].side_effect
        return None
