# -*- coding: utf-8 -*-
from src.parser.parseNode import ParseNode

debug_mode = False


class LeafNode(ParseNode):
    def __init__(self, lexical_form, lemma, msi):
        if debug_mode: print("--> LeafNode.init()")
        ParseNode.__init__(self)
        self.lexical_form = lexical_form.lower()
        self.original_lexical_form = lexical_form
        self.lemma = lemma
        self.msi = msi

    def components(self):
        if debug_mode: print("--> LeafNode.components()")
        return self.lexical_form.split("_")

    def original_components(self):
        if debug_mode: print("--> LeafNode.original_components")
        return self.original_lexical_form.split("_")

    def joined_text(self):
        if debug_mode: print("--> LeafNode.joined_text")
        return " ".join(self.original_components())

    def lemma_matches(self, lemmas):
        if debug_mode: print("--> LeafNode.lemma_matches")
        return self.lemma in lemmas

    def lexical_form_matches(self, lexical_forms):
        if debug_mode: print("--> LeafNode.lexical_form_matches")
        return self.lexical_form in lexical_forms

    def size(self):
        if debug_mode: print("--> LeafNode.size")
        return len(self.components())

    def __repr__(self):
        if debug_mode: print("--> LeafNode.repr()")
        return self.original_lexical_form

    def is_equivalent_to(self, other):
        if debug_mode: print("--> LeafNode.is_equivalent_to")
        try:
            attributes = ["lexical_form", "lemma", "msi"]
            return all(self.__dict__[attribute] == other.__dict__[attribute] for attribute in attributes) \
                   and ParseNode.is_equivalent_to(self, other)
        except KeyError:
            return False