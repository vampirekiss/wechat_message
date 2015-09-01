# -*- coding: utf-8 -*-
from __future__ import absolute_import

from tornado.options import define, options
from tornado.ioloop import IOLoop
from app.api.token import TokenHandler
from app.api.message import MessageHandler
from app.api.menu import MenuHandler
from app.views.menu import MenuViewHandler
from app.provider import ServiceProvider

import json
import os


define("address", default="127.0.0.1", type=str, help="server address to bind on")
define("port", default=9001, type=int, help="server port to bind on")
define("debug", default=False, help="run in debug mode", type=bool)

options.parse_command_line()

config_file = '{}/config.json'.format(os.path.dirname(__file__))

if not os.path.isfile(config_file):
    raise Exception("config file {} not found!".format(config_file))

with open(config_file) as f:
    config = json.load(f)

_service_provider = ServiceProvider(IOLoop.current(), config)

request_handlers = [
    # API handlers
    (
        r"/api/v1/getAccessToken", TokenHandler,
        dict(
            wechat_access_token_provider=_service_provider.wechat_access_token_provider,
            token_request_validator=_service_provider.token_request_validator
        )
    ),
    (
        r"/api/v1/message", MessageHandler,
        dict(
            wechat_request_validator=_service_provider.wechat_request_validator,
            wechat_message_proxy=_service_provider.wechat_message_proxy
        )
    ),
    (
        r"/api/v1/menu", MenuHandler,
        dict(
            wechat_client=_service_provider.wechat_client,
            wechat_access_token_provider=_service_provider.wechat_access_token_provider
        )
    ),
    # view handlers
    (
        r"/menu", MenuViewHandler,
        dict(
            wechat_client=_service_provider.wechat_client,
            wechat_access_token_provider=_service_provider.wechat_access_token_provider
        )
    )
]

app_options = options
