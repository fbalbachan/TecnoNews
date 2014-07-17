# -*- coding: utf-8 -*-

class GlobalOperator:
    def __init__(self, klass, object = None):  # @ReservedAssignment
        self.klass = klass
        self.object = object

    def __repr__(self):
        return self.klass + ((" " + str(self.object)) if self.object else "")

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __hash__(self):
        return hash(tuple(self.__dict__.values()))

    @staticmethod
    def For(object = None, *classes):  # @ReservedAssignment
        operators = []
        for klass in classes:
            operators.append(GlobalOperator(klass, object))
        return operators

    classes = [ "negation", "volitive", "question", "possibility", "imperative", "condition", "future"]