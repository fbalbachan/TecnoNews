# -*- coding: utf-8 -*-
from src.model.tacitEntity import TacitEntity

class Entity (TacitEntity):

    def __init__(self, node):
        TacitEntity.__init__(self, node.leaves_string(), {})
        self.node = node

    def level(self):
        return self.node.level()

    def leaves(self):
        return self.node.leaves()

    def contains(self, other):
        return self.node.contains(other.node)

    def category(self):
        return self.msi["category"]

    def highest_subordinating_level(self):
        return self.highest_subordinating_node().level()

    def highest_subordinating_node(self):
        return sorted(self.subordinating_nodes(), key = lambda node: node.level())[0]

    def is_subordinated(self):
        return bool(self.subordinating_nodes())

    def subordinating_nodes(self):
        path_to_root = self.node.path_to_root()
        return filter(lambda node: node.label in [ "coor-sp", "grup-sp", "sp-de" ], path_to_root)

    def __repr__(self):
        return " ".join([ str(leaf) for leaf in self.node.leaves() ])