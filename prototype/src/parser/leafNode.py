# -*- coding: utf-8 -*-

from parseNode import *


class LeafNode(ParseNode):
    def __init__(self, lexical_form, lemma, msi):
        ParseNode.__init__(self)
        self.lexical_form = lexical_form.encode("utf-8")
        self.lemma = lemma.encode("utf-8")
        self.msi = msi

    def __repr__(self):
        return self.lexical_form

    def is_equivalent_to(self, other):
        try:
            attributes = ["lexical_form", "lemma", "msi"]
            return all( self.__dict__[attribute] == other.__dict__[attribute] for attribute in attributes) and \
                ParseNode.is_equivalent_to(self, other)
        except KeyError:
            return False
