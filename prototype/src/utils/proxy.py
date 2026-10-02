#-*- coding: utf-8 -*-

from types import MethodType

class Proxy(object):

    def __init__(self, target):
        self._target = target

    def __getattr__(self, aname):
        target = self._target
        f = getattr(target, aname)
        if isinstance(f, MethodType):
            # Rebind the method to the target.
            return MethodType(f.__func__, self)
        else:
            return f