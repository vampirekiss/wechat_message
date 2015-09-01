# -*- coding: utf-8 -*-

from glob import glob

import unittest
import tornado.testing
import logging


def all():
    test_modules = list(map(lambda x: x.rstrip('.py').replace('/', '.'),
                            glob('tests/**/*.py')))
    return unittest.defaultTestLoader.loadTestsFromNames(test_modules)


def disable_log():
    hn = logging.NullHandler()
    hn.setLevel(logging.DEBUG)
    for name in ["access", "application", "general"]:
        logger = logging.getLogger("tornado.{}".format(name))
        logger.addHandler(hn)
        logger.propagate = False

if __name__ == "__main__":
    disable_log()
    tornado.testing.main()