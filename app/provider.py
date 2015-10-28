# -*- coding: utf-8 -*-
from __future__ import absolute_import

from cached_property import cached_property
from redis import StrictRedis
from app.wechat.client import WechatClient
from app.wechat.message import WechatMessageParser, WechatMessageRequestValidator, WechatEventSetting
from app.wechat import token
from app.proxy import WechatMessageProxy
from app.proxy.event import WechatReplyTextMessageHandler, WechatMassSendJobFinishHandler
from app.proxy.worker import WechatMessageProxyWorker
from app.proxy.targets import live800

import os


class ServiceProvider(object):

    _base_path = os.path.dirname(__file__)

    def __init__(self, io_loop, config):
        self.config = config
        self.io_loop = io_loop

    @cached_property
    def wechat_access_token_provider(self):
        # return token.WechatAccessTokenProvider(self.wechat_client)
        config = self.config.get('missfresh')
        return token.MissFreshAccessTokenProvider(
            config.get('token'), config.get('api_url')
        )

    @cached_property
    def wechat_client(self):
        config = self.config.get('wechat')
        return WechatClient(
            config.get('api_url'), config.get('app_id'), config.get('secret')
        )

    @cached_property
    def wechat_request_validator(self):
        config = self.config.get('wechat')
        return WechatMessageRequestValidator(config.get('token'))

    @cached_property
    def wechat_event_setting(self):
        setting_file = self.config.get('event_setting_file', '{}/event_setting.cfg'.format(self._base_path))
        return WechatEventSetting(setting_file)

    @cached_property
    def wechat_message_proxy(self):
        wechat_event_handlers = [
            WechatReplyTextMessageHandler(
                self.wechat_client, self.wechat_event_setting
            ),
            WechatMassSendJobFinishHandler(self.redis)
        ]
        return WechatMessageProxy(
            self.wechat_access_token_provider,
            WechatMessageParser(),
            self.wechat_message_proxy_worker,
            wechat_event_handlers
        )

    @cached_property
    def wechat_message_proxy_worker(self):
        config = self.config.get('live800')
        proxy_targets = [
            live800.ProxyTarget(
                config.get('token'), config.get('api_url')
            )
        ]
        return WechatMessageProxyWorker(self.io_loop, proxy_targets)

    @cached_property
    def token_request_validator(self):
        config = self.config.get('live800')
        return live800.TokenRequestValidator(config.get('token'))

    @cached_property
    def redis(self):
        redis_config = self.config.get('redis')
        redis = StrictRedis(
            redis_config.get('host'), redis_config.get('port'), redis_config.get('db')
        )
        redis.ping()
        return redis
