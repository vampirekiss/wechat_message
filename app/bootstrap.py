# -*- coding: utf-8 -*-
from __future__ import absolute_import

from tornado.options import define, options
from tornado.ioloop import IOLoop
from app.api.token import TokenHandler
from app.api.message import MessageHandler
from app.api.menu import MenuHandler
from app.api.event_setting import EventSettingHandler
from app.views.menu import MenuViewHandler
from app.views.event_setting import EventSettingViewHandler
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

_user, _password = tuple(config.get('auth').get('basic'))
_basic_auth_compare_func = lambda u, p: u == _user and p == _password

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
            auth_compare_func=_basic_auth_compare_func,
            wechat_client=_service_provider.wechat_client,
            wechat_access_token_provider=_service_provider.wechat_access_token_provider
        )
    ),
    (
        r"/api/v1/event-setting", EventSettingHandler,
        dict(
            auth_compare_func=_basic_auth_compare_func,
            wechat_event_setting=_service_provider.wechat_event_setting
        )
    ),
    # view handlers
    (
        r"^/$|/menu", MenuViewHandler,
        dict(
            auth_compare_func=_basic_auth_compare_func,
            wechat_client=_service_provider.wechat_client,
            wechat_access_token_provider=_service_provider.wechat_access_token_provider
        )
    ),
    (
        r"/event-setting", EventSettingViewHandler,
        dict(
            auth_compare_func=_basic_auth_compare_func,
            wechat_event_setting=_service_provider.wechat_event_setting
        )
    )
]

app_options = options
