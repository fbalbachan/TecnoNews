# -*- coding: utf-8 -*-
from src.utils.stringUtils import set_first_letter_case


class Rewrite:
    def __init__(self, node, replacement):
        self.node = node
        self.replacement = replacement

    def token(self):
        return self.node.token

    def overlaps(self, other):
        return self.token().overlaps(other.token())

    def __repr__(self):
        return self.node.leaves_string() + " -> " + self.replacement

    @staticmethod
    def preserving_case(node, replacement):
        leaf = node.leaves()[0]
        replacement = set_first_letter_case(leaf.original_lexical_form, replacement)
        return Rewrite(node, replacement)