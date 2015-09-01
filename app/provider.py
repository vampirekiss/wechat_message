# -*- coding: utf-8 -*-
from __future__ import absolute_import

from cached_property import cached_property
from app.wechat.client import WechatClient
from app.wechat.message import WechatMessageParser, WechatMessageRequestValidator
from app.wechat import token
from app.proxy import WechatMessageProxy
from app.proxy.worker import WechatMessageProxyWorker
from app.proxy.targets import live800


class ServiceProvider(object):
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
    def wechat_message_proxy(self):
        return WechatMessageProxy(
            self.wechat_message_proxy_worker,
            WechatMessageParser()
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