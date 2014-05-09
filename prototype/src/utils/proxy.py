#-*- coding: utf-8 -*-

import new
from types import MethodType

class Proxy(object):

    def __init__(self, target):
        self._target = target

    def __getattr__(self, aname):
        target = self._target
        f = getattr(target, aname)
        if isinstance(f, MethodType):
            # Rebind the method to the target.
            return new.instancemethod(f.im_func, self, target.__class__)
        else:
            return f