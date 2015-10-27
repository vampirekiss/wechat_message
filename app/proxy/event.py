# -*- coding: utf-8 -*-
from __future__ import absolute_import

from abc import ABCMeta, abstractmethod
from tornado.gen import coroutine
from app.wechat.message import WechatEventSetting
from xml.etree import ElementTree

import json

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


class WechatMassSendJobFinishHandler(WechatEventHandler):
    def __init__(self, redis):
        self.redis = redis

    @coroutine
    def _handle(self, access_token, message):
        if message.event_type != 'MASSSENDJOBFINISH':
            return

        et = ElementTree.fromstring(message.xml)

        msg_id = et.find('MsgID').text

        callback_info = {
            'sent_count': et.find('SentCount').text,
            'error_count': et.find('ErrorCount').text
        }

        self.redis.hset('msg_call_back', msg_id, json.dumps(callback_info))
