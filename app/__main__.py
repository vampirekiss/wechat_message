# -*- coding: utf-8 -*-
from __future__ import absolute_import

from app.application import Application


if __name__ == '__main__':

    try:
        Application().start()
    except KeyboardInterrupt:
        pass