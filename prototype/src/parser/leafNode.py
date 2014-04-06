# -*- coding: utf-8 -*-

from parseNode import *


class LeafNode(ParseNode):
    def __init__(self, lexicalForm, lemma, msi):
        ParseNode.__init__(self)
        self.lexicalForm = lexicalForm
        self.lemma = lemma
        self.msi = msi

    def __repr__(self):
        return self.lexicalForm.encode("utf-8")

    def is_equivalent_to(self, other):
        try:
            attributes = ["lexicalForm", "lemma", "msi"]
            return all( self.__dict__[attribute] == other.__dict__[attribute] for attribute in attributes) and \
                ParseNode.is_equivalent_to(self, other)
        except KeyError:
            return False
