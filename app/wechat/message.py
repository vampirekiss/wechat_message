# -*- coding: utf-8 -*-
from __future__ import absolute_import

from xml.etree import ElementTree

import hashlib
import pickle


class WechatEventType(object):
    Subscribe = 'subscribe'
    Unsubscribe = 'unsubscribe'


class WechatMessage(object):
    def __init__(self, message_xml, from_user_name, message_id=None, event_type=None):
        self.xml = message_xml
        self.from_user_name = from_user_name
        self.id = message_id
        self.event_type = event_type

    def is_event(self):
        return self.event_type is not None

    def is_subscribe_event(self):
        return self.event_type == WechatEventType.Subscribe

    def is_unsubscribe_event(self):
        return self.event_type == WechatEventType.Unsubscribe

    def __repr__(self):
        if self.is_event():
            return '<WechatMessage Event {}>'.format(self.event_type)
        else:
            return '<WechatMessage Message #{} event type {}>'.format(self.id, self.event_type)


class WechatMessageParser(object):
    def parse(self, message_xml):
        try:
            et = ElementTree.fromstring(message_xml)
            from_user_name = et.find('FromUserName').text
            message_id_node = et.find('MsgId')
            if message_id_node is not None:
                return WechatMessage(message_xml, from_user_name, message_id=message_id_node.text)
            message_event_node = et.find('Event')
            if message_event_node is not None:
                return WechatMessage(message_xml, from_user_name, event_type=message_event_node.text)
            return None
        except:
            return None


class WechatMessageRequestValidator(object):
    def __init__(self, token):
        self.token = token

    def validate_signature(self, signature, timestamp, nonce):
        params = [self.token, timestamp, nonce]
        params.sort()
        valid_sign = str(hashlib.sha1(u''.join(params)).hexdigest())
        return valid_sign == signature


class WechatEventSetting(object):
    Subscribe_Reply_Text = 'subscribe_reply_text'

    all_settings = [
        Subscribe_Reply_Text,
    ]

    def __init__(self, setting_file=None, setting=None):

        if setting_file is None and setting is None:
            raise ValueError("setting_file or setting is required")
        if setting and type(setting) is not dict:
            raise ValueError("setting must be a dict instance")

        if setting_file:
            try:
                with open(setting_file) as f:
                    setting = pickle.load(f)
            except:
                setting = {}

        self._setting_file = setting_file
        self._setting = self._merge_setting(setting)

    def _merge_setting(self, setting):
        merged_setting = {}
        for key in self.all_settings:
            merged_setting[key] = None
        merged_setting.update(setting)
        return merged_setting

    def get_all(self):
        return self._setting

    def get(self, key, default=None):
        return self._setting.get(key, default)

    def set(self, key, value):
        self._setting[key] = value

    def set_all(self, setting):
        self._setting = setting.copy()

    def save(self):
        if self._setting_file is None:
            return
        with open(self._setting_file, 'w') as f:
            pickle.dump(self._setting, f)