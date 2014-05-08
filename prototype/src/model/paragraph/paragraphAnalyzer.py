# -*- coding: utf-8 -*-
from src.model.sentence.sentenceAnalyzer import SentenceAnalyzer


class ParagraphAnalyzer:
    def __init__(self, sentenceAnalyzer = SentenceAnalyzer()):
        self.sentenceAnalyzer = sentenceAnalyzer
        self.context = sentenceAnalyzer.context

    def analyze(self, paragraph):
        self.context["sentences"] = []

        for sentence in paragraph.sentences:
            self.sentenceAnalyzer.analyze(sentence)
            self.context["sentences"].append(sentence)