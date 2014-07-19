# -*- coding: utf-8 -*-
from src.model.entity.tacitEntity import TacitEntity

class Entity (TacitEntity):

    def __init__(self, node):
        self.node = node
        self.kernel = None
        self.father = None
        self.proper_node = None

        TacitEntity.__init__(self, self.lexical_form(), {}, [])

    def is_subordinated_with_preposition(self, preposition):
        father = self.node.father
        return father.label in [ "grup-sp", "sp-de" ] and father.leaves()[0].lexical_form == preposition

    def level(self):
        return self.node.level()

    def leaves(self):
        return self.node.leaves()

    def contains(self, other):
        return other in self.children

    def highest_subordinating_level(self):
        return self.highest_subordinating_node().level()

    def highest_subordinating_node(self):
        return sorted(self.subordinating_nodes(), key = lambda node: node.level())[0]

    def header(self):
        if not self.is_subordinated(): return None
        node = self.highest_subordinating_node()
        first_leaf = node.leaves()[0]
        if first_leaf.msi["type"] != "preposition": return None
        return first_leaf

    def is_subordinated(self):
        return bool(self.subordinating_nodes())

    def subordinating_nodes(self):
        path_to_root = self.node.path_to_root()
        return filter(lambda node: node.label in [ "coor-sp", "grup-sp", "sp-de", "grup-sp-inf" ], path_to_root)

    def is_tacit(self):
        return False

    def lexical_form(self):
        return " ".join([ str(leaf) for leaf in self.node.leaves() if leaf.msi["category"] != "punctuation" ])

    def __repr__(self):
        representation = self.lexical_form
        if self.is_possessed(): representation = representation + " (of " + repr(self.owner) + ")"
        return representation

    @staticmethod
    def only_maximal(entities):
        return filter(lambda entity: not any([ other.contains(entity) for other in entities ]), entities)