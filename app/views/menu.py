# -*- coding: utf-8 -*-
from __future__ import absolute_import

from app.api.menu import MenuHandler
from app.views import ViewHandlerMixin


class MenuViewHandler(MenuHandler, ViewHandlerMixin):

    _view_name = 'menu'

    def _output_menu_response(self, menu):
        buttons = menu.get('button', [])
        self.render_template('menu.html', buttons=buttons)

    def post(self):
        self.request.body = '{"button":%s}' % self.request.body
        return super(MenuViewHandler, self).post()


