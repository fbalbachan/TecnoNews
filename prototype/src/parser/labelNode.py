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

    def label_lemma_matches(self, labels, lemmas):
        matches = True
        if labels is not None:
            matches = matches and self.label in labels

        matches = matches \
                  and len(self.children) == 1 \
                  and self.children[0].is_leaf() \
                  and self.children[0].lemma_matches(lemmas)

        return matches
