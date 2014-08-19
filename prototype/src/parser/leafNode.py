# -*- coding: utf-8 -*-
from src.parser.parseNode import ParseNode


class LeafNode(ParseNode):
    def __init__(self, lexical_form, lemma, msi):
        ParseNode.__init__(self)
        self.lexical_form = lexical_form.lower()
        self.original_lexical_form = lexical_form
        self.lemma = lemma
        self.msi = msi

    def components(self):
        return self.lexical_form.split("_")

    def original_components(self):
        return self.original_lexical_form.split("_")

    def size(self):
        return len(self.components())

    def __repr__(self):
        return self.original_lexical_form

    def is_equivalent_to(self, other):
        try:
            attributes = ["lexical_form", "lemma", "msi"]
            return all( self.__dict__[attribute] == other.__dict__[attribute] for attribute in attributes) and \
                ParseNode.is_equivalent_to(self, other)
        except KeyError:
            return False