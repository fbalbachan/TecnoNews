# -*- coding: utf-8 -*-
from src.utils.stringUtils import *

debug_mode = False


class Rewrite:
    def __init__(self, node, replacement):
        if debug_mode: print("--> Rewrite.init(node:", node, ", replacement:", replacement, ")")
        self.node = node
        self.replacement = replacement

        if debug_mode: print("<-- Rewrite.init()")

    def token(self):
        return self.node.token

    def overlaps(self, other):
        return self.token().overlaps(other.token())

    def __repr__(self):
        represent = self.node.leaves_string() + " -> " + self.replacement
        return represent

    @staticmethod
    def preserving_case(node, replacement):
        if debug_mode: print("--> Rewrite.preserving_case(node:", node, ", replacement:", replacement, ")")
        leaf = node.leaves()[0]
        replacement = set_first_letter_case(leaf.original_lexical_form, replacement)
        rewrite = Rewrite(node, replacement)

        if debug_mode: print("<-- Rewrite.preserving_case()")
        return rewrite
