# -*- coding: utf-8 -*-

from parseNode import *


class LeafNode(ParseNode):
    def __init__(self, lexicalForm, lemma, msi):
        ParseNode.__init__(self)
        self.lexicalForm = lexicalForm
        self.lemma = lemma
        self.msi = msi

    def set_father(self, labelNode):
        self.father = labelNode

    def __repr__(self):
        return self.lexicalForm