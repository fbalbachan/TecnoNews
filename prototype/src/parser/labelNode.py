# -*- coding: utf-8 -*-

from parseNode import *


class LabelNode(ParseNode):
    def __init__(self, label):
        ParseNode.__init__(self)
        self.label = label

    def add_child(self, node):
        self.children.append(node)
        if node.is_root():
            node.set_father(self)

    def __repr__(self):
        return self.label

    def is_equivalent_to(self, other):
        try:
            return self.label == other.label and ParseNode.is_equivalent_to(self, other)
        except AttributeError:
            return False

    def label_lemma_lf_matches(self, labels, lemmas, lexical_forms):
        matches = True
        if labels is not None:
            matches = matches and self.label in labels

        if not (lemmas or lexical_forms) \
           or len(self.children) != 1 or not self.children[0].is_leaf():
            return False

        matches = matches and (not lemmas or self.children[0].lemma_matches(lemmas))
        matches = matches and (not lexical_forms or self.children[0].lexical_form_matches(lexical_forms))

        return matches
