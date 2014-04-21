#-*- coding: utf-8 -*-

from copy import copy
from itertools import groupby

from inDepthNodeIterator import *


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
        if father and not self in father.children:
            father.add_child(self)

    def is_leaf(self):
        return not self.children

    def __init__(self):
        self.father = None
        self.children = []

    def leaves(self):
        return filter(lambda node: node.is_leaf(), self)

    def leaves_of_msi(self, msi):
        return filter(lambda leaf: all([ attribute in leaf.msi and leaf.msi[attribute] == value
                                       for attribute, value in msi.items() ]), self.leaves())

    def leaves_of_category(self, category):
        return self.leaves_of_msi({ "category" : category })

    def leaves_string(self):
        return " ".join([ str(leaf) for leaf in self.leaves() ])

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

    def subordinates_others(self):
        return not self.is_leaf() and self.label in ["subord-rel", "subord"]

    def is_subordinate(self):
        return any( (node.subordinates_others() for node in self.path_to_root()) )

    # El padre no es comparado pues debería complejizarse el método. Sólo el subárbol descendente.
    def is_equivalent_to(self, other):
        if len(self.children) != len(other.children):
            return False
        return all( this.is_equivalent_to(that) for this, that in zip(self.children, other.children))

    # El subárbol devuelto es independiente y es copia profunda del original.
    def cloned_by_original(self, without_nodes):
        iterator = InDepthNodeIterator(self, without_nodes)

        cloned_by_original = {}
        if not self.is_root():
            cloned_by_original[self.father] = None

        for original_node in iterator:
            cloned = copy(original_node)

            if not original_node.is_root():
                cloned_father = cloned_by_original[original_node.father]
                cloned.set_father(cloned_father)

            cloned.children = []

            cloned_by_original[original_node] = cloned
        return cloned_by_original

    def label_node_chlidren(self):
        return filter(lambda child: not child.is_leaf(), self.children)

    def root(self):
        node = self
        while not node.is_root():
            node = node.father
        return node

    def leaf_positions(self):
        leaf_positions = { leaf: index for (index, leaf) in enumerate(self.root().leaves()) }
        return sorted([ leaf_positions[leaf] for leaf in self.leaves() ])

    def position_of(self, node):
        proper_positions = self.leaf_positions()
        other_positions = node.leaf_positions()

        if proper_positions[0] < other_positions[0]     : return "right"
        if proper_positions[-1] > other_positions[-1]   : return "left"
        return "inside"

    def absolute_distance_to(self, node):
        return abs(self.distance_to(node))

    def distance_to(self, node):
        if self.level() != node.level(): raise Exception("Los nodos no son hermanos.")
        brothers = self.father.children
        return brothers.index(node) - brothers.index(self)

    @staticmethod
    def by_level(nodes):
        level_getter = lambda node: node.level()
        by_level = groupby(sorted(nodes, key=level_getter), level_getter)
        by_level = { level: list(nodes) for level, nodes in by_level }
        return by_level