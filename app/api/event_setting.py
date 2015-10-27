# -*- coding: utf-8 -*-
from __future__ import absolute_import

from tornado.gen import coroutine
from tornado.locks import Lock
from app.api import BasicAuthHandlerMixin
from app.wechat.message import WechatEventSetting

import json


class EventSettingHandler(BasicAuthHandlerMixin):
    def initialize(self, wechat_event_setting, **kwargs):
        super(EventSettingHandler, self).initialize(**kwargs)
        self.wechat_event_message_setting = wechat_event_setting
        self.setting_lock = Lock()

    def _output_setting(self, setting):
        response = {
            'setting': setting
        }
        self.write(response)

    @coroutine
    def get(self):
        setting = self.wechat_event_message_setting.get_all()
        self._output_setting(setting)

    @coroutine
    def post(self):
        json_str = self.request.body
        try:
            setting = json.loads(json_str)
        except:
            self._output_error_response(400, 'bad request')
            return

        for key in setting:
            if key not in WechatEventSetting.all_settings:
                self._output_error_response(400, 'setting has no key "{}"'.format(key))
                return

        with (yield self.setting_lock.acquire()):
            self.wechat_event_message_setting.set_all(setting)
            self.wechat_event_message_setting.save()

        self.write(
            {
                'errcode': 0, 'errmsg': ''
            }
        )