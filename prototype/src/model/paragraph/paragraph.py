# -*- coding: utf-8 -*-
from src.model.sentence.sentenceSplitter import SentenceSplitter

class Paragraph:
    def __init__(self, sentences):
        self.sentences = sentences

    def clauses(self):
        return sum([ sentence.clauses for sentence in self.sentences ], [])

    @staticmethod
    def from_text(text):
        sentences = SentenceSplitter().sentences_in(text)
        return Paragraph(sentences)