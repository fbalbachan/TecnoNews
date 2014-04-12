# -*- coding: utf-8 -*-

class Entity:
    def __init__(self, node):
        self.node = node
        self.msi = {}

    def level(self):
        return self.node.level()

    def leaves(self):
        return self.node.leaves()

    def contains(self, other):
        return self.node.contains(other.node)

    def category(self):
        return self.msi["category"]

    def __repr__(self):
        return " ".join([ str(leaf) for leaf in self.node.leaves() ])