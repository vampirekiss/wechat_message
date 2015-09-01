# -*- coding: utf-8 -*-


class ViewHandlerMixin(object):
    flashed_messages = []

    def render_template(self, template_name, **kwargs):
        kwargs["request_path"] = self.request.path
        kwargs["get_flashed_messages"] = self.get_flashed_messages
        self.render(template_name, **kwargs)

    def flash(self, message, category='info'):
        self.flashed_messages.append((category, message))

    def get_flashed_messages(self):
        result = self.flashed_messages
        self.flashed_messages = []
        return result