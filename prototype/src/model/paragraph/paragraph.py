# -*- coding: utf-8 -*-
from src.model.sentence.sentenceSplitter import SentenceSplitter

class Paragraph:
    def __init__(self, sentences = [], text = ""):
        self.sentences = sentences
        self.text = text

    def clauses(self):
        return sum([ sentence.clauses for sentence in self.sentences ], [])

    def entities(self):
        return sum([ clause.all_entities() for clause in self.clauses() ], [])

    def referents(self):
        return set([ entity.referent for entity in self.entities() ])

    def named_referents(self):
        return { referent for referent in self.referents() if referent.semantic_classification() }

    def clauses_for(self, referent):
        return filter(lambda clause: any( ( referent == entity.referent for entity in clause.all_entities()) ), \
                      self.clauses())

    def facts_for(self, referent):
        return filter(lambda clause: clause.is_fact(), self.clauses_for(referent))

    @staticmethod
    def from_text(text):
        # TODO: Repensar desde la arquitectura si las sentences son de text o del párrafo,
        #       ya que Paragraph(sentences, text) puede ser redundante.
        paragraph = Paragraph()
        # Mientras tanto, paragraph es un parámetro -posiblemente redundante-
        # de SentenceSplitter.sentences_in()
        sentences = SentenceSplitter().sentences_in(text, paragraph)
        paragraph.sentences = sentences
        paragraph.text = text
        return paragraph