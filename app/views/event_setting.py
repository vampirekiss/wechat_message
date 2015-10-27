# -*- coding: utf-8 -*-
from __future__ import absolute_import

from app.api.event_setting import EventSettingHandler
from app.views import ViewHandlerMixin


class EventSettingViewHandler(EventSettingHandler, ViewHandlerMixin):

    _view_name = 'event-setting'

    def _output_setting(self, setting):
        self.render_template('event_setting.html', setting=setting)