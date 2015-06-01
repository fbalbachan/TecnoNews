# -*- coding: utf-8 -*-
from copy import copy

from src.utils.tree.inDepthNodeIterator import InDepthNodeIterator
from src.utils.collectionUtils import dict_by

debug_mode = False


class TreeNode:

    def __init__(self):
        self.father = None
        self.children = []

    def __iter__(self):
        return InDepthNodeIterator(self)

    def leaves(self, iterator=InDepthNodeIterator):
        if debug_mode: print "--> TreeNode.leaves()"
        return filter(lambda node: node.is_leaf(), iterator(self))

    def is_subordinated(self):
        return not self.is_root()

    def is_leaf(self):
        return not self.children

    def level(self):
        level = 0
        father = self.father
        while father:
            level += 1
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

    def tree_representation(self):
        return self.tree_representation_for(self, "", "")

    def tree_representation_for(self, root, pad, representation):
        index = list(root).index(self)
        level = self.level()
        str_idx = repr(index).rjust(3) + "," + repr(level).rjust(3) + "  "

        if self.is_leaf():
            representation += str_idx + pad + "[ " + repr(self) + " ]\n"
        else:
            representation += str_idx + pad + repr(self) + "\n"

        pad += "    "
        for child in self.children:
            representation = child.tree_representation_for(root, pad, representation)

        return representation

    # El padre no es comparado pues debería complejizarse el método. Sólo el subárbol descendente.
    def is_equivalent_to(self, other):
        if len(self.children) != len(other.children):
            return False

        is_equivalent = all(this.is_equivalent_to(that) for this, that in zip(self.children, other.children))
        return is_equivalent

    # El subárbol devuelto es independiente y copia profunda del original.
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

    def root(self):
        node = self
        while not node.is_root():
            node = node.father
        return node

    def leaf_positions(self):
        leaf_positions = {leaf: index for (index, leaf) in enumerate(self.root().leaves())}
        return sorted([leaf_positions[leaf] for leaf in self.leaves()])

    def position_of(self, node):
        proper_positions = self.leaf_positions()
        other_positions = node.leaf_positions()

        if proper_positions[0] < other_positions[0]:
            return "right"

        if proper_positions[-1] > other_positions[-1]:
            return "left"

        return "inside"

    def absolute_distance_to(self, node):
        return abs(self.distance_to(node))

    def distance_to(self, node):
        if self.level() != node.level():
            raise Exception("Los nodos no son hermanos.")

        brothers = self.father.children
        return brothers.index(node) - brothers.index(self)

    def contains(self, node):
        for each in self:
            if each is node:
                return True
        return False

    @staticmethod
    def by_level(nodes):
        level_getter = lambda node: node.level()
        return dict_by(nodes, level_getter)
