# -*- coding: utf-8 -*-
from __future__ import absolute_import

from abc import ABCMeta, abstractmethod
from tornado.gen import coroutine
from app.wechat.message import WechatEventSetting


class WechatEventHandler(object):
    __metaclass__ = ABCMeta

    @coroutine
    def handle(self, access_token, message):
        yield self._handle(access_token, message)

    @abstractmethod
    def _handle(self, access_token, message):
        pass


class WechatReplyTextMessageHandler(WechatEventHandler):
    def __init__(self, wechat_client, wechat_event_setting):
        self.wechat_client = wechat_client
        self.wechat_event_setting = wechat_event_setting

    @coroutine
    def _handle(self, access_token, message):

        key = None

        if message.is_subscribe_event():
            key = WechatEventSetting.Subscribe_Reply_Text

        if key is None:
            return

        reply_text = self.wechat_event_setting.get(key)

        if reply_text is None or reply_text == '':
            return

        reply_message = {
            "touser": message.from_user_name,
            "msgtype": "text",
            "text": {
                "content": reply_text
            }
        }

        yield self.wechat_client.send_custom_message(access_token, reply_message)

