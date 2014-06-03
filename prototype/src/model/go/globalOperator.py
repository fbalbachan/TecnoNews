# -*- coding: utf-8 -*-

class GlobalOperator:
    def __init__(self, klass, node = None):
        self.klass = klass
        self.node = node

    def __repr__(self):
        return self.klass + (" " + str(self.node)) if self.node else ""