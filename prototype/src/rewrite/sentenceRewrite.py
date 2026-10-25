# -*- coding: utf-8 -*-
__author__ = 'Alexis Balbachan'

from src.utils.stringUtils import *

debug_mode = False


class SentenceRewrite:
    def __init__(self, sentence_text, sentence_token, replacement_text):
        if debug_mode: print("--> SentenceRewrite.init()")

        self.sentence_text = sentence_text[:]

        self.replacement_text = replacement_text[:]

        self.token = sentence_token

        beginning = self.sentence_text[0:self.token.start()]
        ending = self.sentence_text[self.token.end():]

        self.replacement = beginning + self.replacement_text + ending

    def token(self):
        return self.token

    def overlaps(self, other):
        return self.token().overlaps(other.token())

    def __repr__(self):
        if debug_mode: print("--> SentenceRewrite.repr()")
        represent = self.sentence_text + " --> " + self.replacement
        return represent

    @staticmethod
    def preserving_case(sentence_text, token, replacement_text):

        to_be_replaced = sentence_text[token.start():token.end()]
        replacement_text = set_first_letter_case(to_be_replaced, replacement_text)
        rule = SentenceRewrite(sentence_text, token, replacement_text)
        return rule
