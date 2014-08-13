# -*- coding: utf-8 -*-
from src.model.sentence.sentenceSplitter import SentenceSplitter

class Paragraph:
    def __init__(self, sentences = []):
        self.sentences = sentences

    def clauses(self):
        return sum([ sentence.clauses for sentence in self.sentences ], [])

    def entities(self):
        return sum([ clause.all_entities() for clause in self.clauses() ], [])

    def referents(self):
        return set([ entity.referent for entity in self.entities() ])

    def person_referents(self):
        return { referent.semantic_classification() == "person" for referent in self.referents() }

    @staticmethod
    def from_text(text):
        sentences = SentenceSplitter().sentences_in(text)
        return Paragraph(sentences)