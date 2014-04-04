# -*- coding: utf-8 -*-

from parseNode import *


class LabelNode(ParseNode):
    def __init__(self, label):
        ParseNode.__init__(self)
        self.label = label

    def add_child(self, node):
        self.children.append(node)

    def __repr__(self):
        return self.label
