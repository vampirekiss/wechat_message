# -*- coding: utf-8 -*-
from __future__ import absolute_import

from tornado.web import Application as WebApplication
from tornado.ioloop import IOLoop
from app.bootstrap import request_handlers, app_options
from app.api import ErrorHandler

import os


class Application(WebApplication):

    base_path = os.path.dirname(__file__)

    def __init__(self, handlers=None, options=None, io_loop=None):
        self.options = options or app_options
        self.io_loop = io_loop or IOLoop.instance()

        settings = {
            'debug': self.options.debug,
            'template_path': '{}/views/templates'.format(self.base_path),
            'static_path': '{}/views/static'.format(self.base_path),
            'default_handler_class': ErrorHandler
        }

        handlers = handlers or request_handlers
        super(Application, self).__init__(handlers, **settings)

    def start(self):
        self.listen(self.options.port, self.options.address)
        self.io_loop.start()