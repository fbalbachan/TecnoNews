# -*- coding: utf-8 -*-

class GlobalOperator:
    def __init__(self, klass, object = None):  # @ReservedAssignment
        self.klass = klass
        self.object = object

    def __repr__(self):
        return self.klass + (" " + str(self.object)) if self.object else ""