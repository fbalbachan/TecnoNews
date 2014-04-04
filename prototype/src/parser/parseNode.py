#-*- coding: utf-8 -*-

class ParseNode:
    def set_father(self, labelNode):
        self.father = labelNode

    def is_leaf(self):
        return not self.children

    def __init__(self):
        self.children = []

    def tree_representation(self):
        return self.tree_representation_for("", "")

    def tree_representation_for(self, pad, representation):
        representation = representation  + pad + repr(self) + "\n"
        pad = pad + "  "
        for child in self.children:
            representation = child.tree_representation_for(pad, representation)
        return representation