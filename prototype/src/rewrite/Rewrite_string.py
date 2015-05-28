# -*- coding: utf-8 -*-
__author__ = 'Martín Caramés Abente'


# -*- coding: utf-8 -*-


class StringRewrite:
    def __init__(self, orig_string, token, replacement):
        self.orig_string = orig_string
        self.token = token
        self.replacement = replacement

    def token(self):
        return self.token

    def overlaps(self, other):
        return self.token().overlaps(other.token())

    def __repr__(self):
        token = self.token
        return self.orig_string[token.start():token.end()] + " -> " + self.replacement

    @staticmethod
    def preserving_case(orig_string, token, replacement):
        # leaf = node.leaves()[0]
        # replacement = set_first_letter_case(leaf.original_lexical_form, replacement)
        return StringRewrite(orig_string, token, replacement)