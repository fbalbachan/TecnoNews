# -*- coding: utf-8 -*-
__author__ = 'Martín Caramés Abente'

from src.utils.stringUtils import set_first_letter_case

debug_mode = False


class SentenceRewrite:
    def __init__(self, sentence_text, sentence_token, token_replacement):
        if debug_mode: print "--> SentenceRewrite.init()"

        self.sentence_text = sentence_text[:]
        if type(self.sentence_text) is not unicode:
            self.sentence_text = self.sentence_text.decode("utf-8")

        self.token_replacement = token_replacement[:]
        if type(self.token_replacement) is not unicode:
            self.token_replacement = self.token_replacement.decode("utf-8")

        self.token = sentence_token

        beginning = self.sentence_text[0:self.token.start()]
        ending = self.sentence_text[self.token.end():]

        self.replacement = beginning + self.token_replacement + ending

    def token(self):
        return self.token

    def overlaps(self, other):
        return self.token().overlaps(other.token())

    def __repr__(self):
        return u" --> ".join([self.sentence_text, self.replacement])

    @staticmethod
    def preserving_case(sentence_text, token, token_replacement):
        if type(sentence_text) is not unicode:
            sentence_text = sentence_text.decode("utf-8")

        to_be_replaced = sentence_text[token.start():token.end()]
        token_replacement = set_first_letter_case(to_be_replaced, token_replacement)
        rule = SentenceRewrite(sentence_text, token, token_replacement)
        return rule