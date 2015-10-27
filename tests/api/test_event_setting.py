# -*- coding: utf-8 -*-

from tests import AsyncHTTPTestCase
from app.application import Application
from app.api.event_setting import EventSettingHandler
from app.wechat.message import WechatEventSetting


import json


class EventSettingHandlerTestCase(AsyncHTTPTestCase):
    def setUp(self):
        self.wechat_event_setting = WechatEventSetting(
            setting={
                WechatEventSetting.Subscribe_Reply_Text: 'hahaha'
            }
        )
        self.auth_headers = {
            'Authorization': 'Basic YWRtaW46MTIzNDU2'
        }
        super(EventSettingHandlerTestCase, self).setUp()

    def get_app(self):
        return Application(
            [
                (
                    r"/api/v1/event-setting", EventSettingHandler,
                    dict(
                        auth_compare_func=lambda x, y: x == 'admin' and y == '123456',
                        wechat_event_setting=self.wechat_event_setting
                    )
                )
            ]
        )

    def test_get_setting_without_auth(self):
        response = self.get('/api/v1/event-setting')
        self.assertEqual(401, response.code)

    def test_get_setting(self):
        response = self.get('/api/v1/event-setting', headers=self.auth_headers)
        self.assertEqual(200, response.code)
        self.assertIn('hahaha', response.body)

    def test_update_setting(self):
        response = self.post('/api/v1/event-setting', body='', headers=self.auth_headers)
        self.assertEqual(400, response.code)

        setting = self.wechat_event_setting.get_all()
        setting[WechatEventSetting.Subscribe_Reply_Text] = 'blabla'
        response = self.post(
            '/api/v1/event-setting', body=json.dumps(setting, ensure_ascii=False), headers=self.auth_headers
        )
        self.assertEqual(200, response.code)
        new_setting = self.wechat_event_setting.get(WechatEventSetting.Subscribe_Reply_Text)
        self.assertEqual(new_setting, 'blabla')