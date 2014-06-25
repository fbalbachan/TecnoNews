# -*- coding: utf-8 -*-

class WordSentimentalValue:
    def __init__(self, lemma, value):
        self.lemma = lemma
        self.value = value

    def joined_value(self):
        return self.value[0] - self.value[1]

    def is_neutral(self):
        return self.joined_value() == 0

    def __repr__(self):
        return self.lemma + " " + str(self.value)

    def object(self):
        return self.lemma

    @staticmethod
    def default_for(lemma):
        return WordSentimentalValue(lemma, (0, 0))