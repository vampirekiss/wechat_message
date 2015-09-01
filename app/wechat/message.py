# -*- coding: utf-8 -*-
from __future__ import absolute_import

from xml.etree import ElementTree

import hashlib


class WechatMessage(object):
    def __init__(self, message_xml, message_id):
        self.xml = message_xml
        self.id = message_id

    def __repr__(self):
        return '<WechatMessage object #{}>'.format(self.id)


class WechatMessageParser(object):
    def parse(self, message_xml):
        try:
            et = ElementTree.fromstring(message_xml)
            message_id_node = et.find('MsgId')
            if message_id_node is not None:
                return WechatMessage(message_xml, message_id_node.text)
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