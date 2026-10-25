# -*- coding: utf-8 -*-
from src.utils.configProvider import ConfigProvider
from ast import literal_eval
import logging
from traceback import format_exc


def default_raise_exception():
    Config = ConfigProvider()

    string = dict(Config.items("debug"))["raise_exception"]
    return literal_eval(string)


class Invoker:
    def __init__(self, raise_exception = default_raise_exception()):
        self.raise_exception = raise_exception

    def invoke(self, method, *args):
        try:
            return method(*args)
        except Exception as exception:
            if self.raise_exception:
                print(format_exc())
                raise exception
            logging.getLogger("exceptions").error("[Unraised exception] " + format_exc())
