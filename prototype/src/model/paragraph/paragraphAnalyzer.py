# -*- coding: utf-8 -*-
from src.model.sentence.sentenceAnalyzer import SentenceAnalyzer
from src.utils.invoker import Invoker


class ParagraphAnalyzer:
    def __init__(self, sentenceAnalyzer = SentenceAnalyzer()):
        self.sentenceAnalyzer = sentenceAnalyzer
        self.context = sentenceAnalyzer.context
        self.invoker = Invoker()

    def analyze(self, paragraph):
        self.context["sentences"] = []

        for sentence in paragraph.sentences:
            self.invoker.invoke(self.sentenceAnalyzer.analyze, sentence)
            self.context["sentences"].append(sentence)