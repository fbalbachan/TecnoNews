# -*- coding: utf-8 -*-
from src.utils.tree.treeNode import TreeNode


class SentimentalValuedObject(TreeNode):
    def __init__(self, object, value=(0,0), global_operator=None):  # @ReservedAssignment
        TreeNode.__init__(self)
        self.object = object
        self.value = value
        self.global_operator = global_operator

    def joined_value(self):
        return self.value[0] - self.value[1]

    def is_neutral(self):
        return self.joined_value() == 0

    def apply_coef(self, coef):
        value = (int(self.value[0] * abs(coef)), int(self.value[1] * abs(coef)))
        if coef < 0: value = (value[1], value[0])
        self.value = value

    def __repr__(self):
        output = str(self.object) + " " + str(self.joined_value())
        if self.global_operator is not None:
            output += " (" + str(self.global_operator) + ")"
        return output

    @staticmethod
    def cloned(other, coef = 1, global_operator=None):
        clone = SentimentalValuedObject(other.object, other.value, global_operator)
        clone.apply_coef(coef)
        return clone

