# -*- coding: utf-8 -*-
from src.utils.tree.treeNode import TreeNode


class SentimentalValuedObject(TreeNode):
    def __init__(self, object, value=(0,0)):  # @ReservedAssignment
        TreeNode.__init__(self)
        self.object = object
        self.value = value

    def joined_value(self):
        return self.value[0] - self.value[1]

    def is_neutral(self):
        return self.joined_value() == 0

    def apply_coef(self, coef):
        value = (int(self.value[0] * abs(coef)), int(self.value[1] * abs(coef)))
        if coef < 0: value = (value[1], value[0])
        self.value = value

    def __repr__(self):
        return str(self.object) + " " + str(self.joined_value())

    @staticmethod
    def cloned(other, coef = 1):
        clone = SentimentalValuedObject(other.object, other.value)
        clone.apply_coef(coef)
        return clone

