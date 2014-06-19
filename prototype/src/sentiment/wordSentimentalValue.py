# -*- coding: utf-8 -*-

class WordSentimentalValue:
    def __init__(self, lemma, value):
        self.lemma = lemma
        self.value = value

    def __repr__(self):
        return self.lemma + " " + str(self.value)

    @staticmethod
    def default_for(lemma):
        return WordSentimentalValue(lemma, 0)