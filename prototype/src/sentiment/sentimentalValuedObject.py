# -*- coding: utf-8 -*-

class SentimentalValuedObject:
    def __init__(self, object, value = (0,0)):  # @ReservedAssignment
        self.object = object
        self.value = value

    def joined_value(self):
        return self.value[0] - self.value[1]

    def is_neutral(self):
        return self.joined_value() == 0

    def __repr__(self):
        return str(self.object) + " " + str(self.joined_value())