# -*- coding: utf-8 -*-
__author__ = 'Alexis Balbachan'

from src.utils.stringUtils import *

debug_mode = False


class SentenceRewrite:
    def __init__(self, sentence_text, sentence_token, replacement_text):
        if debug_mode: print "--> SentenceRewrite.init()"

        self.sentence_text = sentence_text[:]
        if not has_type_encoding(self.sentence_text, unicode):
            self.sentence_text = self.sentence_text.decode("utf-8")

        self.replacement_text = replacement_text[:]
        if not has_type_encoding(self.replacement_text, unicode):
            self.replacement_text = self.replacement_text.decode("utf-8")

        self.token = sentence_token

        beginning = self.sentence_text[0:self.token.start()]
        ending = self.sentence_text[self.token.end():]

        self.replacement = beginning + self.replacement_text + ending

    def token(self):
        return self.token

    def overlaps(self, other):
        return self.token().overlaps(other.token())

    def __repr__(self):
        if debug_mode: print "--> SentenceRewrite.repr()"
        represent = self.sentence_text.encode("utf-8") + " --> " + self.replacement.encode("utf-8")
        return represent

    @staticmethod
    def preserving_case(sentence_text, token, replacement_text):
        if not has_type_encoding(sentence_text, unicode):
            sentence_text = sentence_text.decode("utf-8")

        to_be_replaced = sentence_text[token.start():token.end()]
        replacement_text = set_first_letter_case(to_be_replaced, replacement_text)
        rule = SentenceRewrite(sentence_text, token, replacement_text)
        return rule
