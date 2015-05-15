# -*- coding: utf-8 -*-
from src.model.entity.tacitEntity import TacitEntity
from src.model.tokenization.token import Token
from collections import deque


class Entity (TacitEntity):

    def __init__(self, node):
        self.node = node
        self.kernel = None
        self.father = None
        self.proper_node = None
        self.token = self.build_token()

        if self.lexical_form().lower() in ["se", "le", "les"]:
            attributes = {"useless": None}
        else:
            attributes = {}

        TacitEntity.__init__(self, self.lexical_form(), {}, attributes)

    def is_subordinated_with_preposition(self, preposition):
        father = self.node.father
        return father.label in ["grup-sp", "sp-de"] and father.leaves()[0].lexical_form == preposition

    def level(self):
        return self.node.level()

    def leaves(self):
        return self.node.leaves()

    def highest_subordinating_level(self):
        return self.highest_subordinating_node().level()

    def highest_subordinating_node(self):
        return sorted(self.subordinating_nodes(), 
                      key=lambda node: node.level())[0]

    def header(self):
        if not self.is_subordinated():
            return None
        node = self.highest_subordinating_node()
        first_leaf = node.leaves()[0]
        if first_leaf.msi["type"] != "preposition": 
            return None
        return first_leaf

    def is_subordinated(self):
        return bool(self.subordinating_nodes())

    def subordinating_nodes(self):
        path_to_root = self.node.path_to_root()
        return filter(lambda node:
                            node.label in ["coor-sp", "grup-sp", "sp-de", "grup-sp-inf"],
                      path_to_root)

    def is_tacit(self):
        return False

    def is_implicit(self):
        return False

    def lexical_form(self):
        return " ".join([str(leaf) for leaf in self.node.leaves() if leaf.msi["category"] != "punctuation"])

    def build_token(self):
        token = Token()
        token.components = [(leaf.token.start(), leaf.token.end()) for leaf in self.node.leaves()
                            if leaf.lexical_form not in [","]]
        return token

    def __repr__(self):
        _repr = self.lexical_form
        if self.is_possessed():
            _repr += " (of " + repr(self.owner) + ")"
        if self.is_linked():
            _repr += " (" + self.referenced().lexical_form + ")"
        return _repr

    def name(self):
        return repr(self.kernel if self.kernel else self)

    @staticmethod
    def only_maximal(entities):
        maximal = filter(lambda entity:
                            not any([other.contains(entity) for other in entities]),
                         entities)
        return maximal

    def get_nested_entities(self, include_myself=False):
        nested_entities = []
        q = deque()

        if include_myself:
            nested_entities.append(self)

        q.extend(self.children)
        while len(q) > 0:
            next_entity = q.popleft()
            nested_entities.append(next_entity)
            q.extend(next_entity.children)

        return nested_entities
