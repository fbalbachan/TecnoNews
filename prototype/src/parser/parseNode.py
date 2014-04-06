#-*- coding: utf-8 -*-

from inDepthNodeIterator import *
from itertools import groupby

class ParseNode:
    def level(self):
        level = 0
        father = self.father
        while father:
            level = level + 1
            father = father.father
        return level

    def path_to_root(self):
        path = []
        node = self
        while not node.is_root():
            node = node.father
            path.append(node)
        return path

    def is_root(self):
        return self.level() == 0

    def set_father(self, father):
        self.father = father
        if not self in father.children:
            father.add_child(self)

    def is_leaf(self):
        return not self.children

    def __init__(self):
        self.father = None
        self.children = []

    def leaves(self):
        return filter(lambda node: node.is_leaf(), self)

    def contains(self, node):
        for each in self:
            if each is node: return True
        return False

    def nodes_with_labels(self, labels):
        nodes = []
        for node in self:
            if not node.is_leaf() and node.label in labels:
                nodes.append(node)
        return nodes

    def __iter__(self):
        return InDepthNodeIterator(self)

    def tree_representation(self):
        return self.tree_representation_for("", "")

    def tree_representation_for(self, pad, representation):
        representation = representation  + pad + repr(self) + "\n"
        pad = pad + "  "
        for child in self.children:
            representation = child.tree_representation_for(pad, representation)
        return representation

    def is_subordinate(self):
        return not self.is_root() and self.father.label in ["subord-rel", "subord"]

    # El padre no es comparado pues debería complejizarse el método. Sólo el subárbol descendente.
    def is_equivalent_to(self, other):
        if len(self.children) != len(other.children):
            return False
        return all( this.is_equivalent_to(that) for this, that in zip(self.children, other.children))

    @staticmethod
    def by_level(nodes):
        level_getter = lambda node: node.level()
        by_level = groupby(sorted(nodes, key=level_getter), level_getter)
        by_level = { level: list(nodes) for level, nodes in by_level }
        return by_level