# -*- coding: utf-8 -*-
from src.model.sentence.sentenceAnalyzer import SentenceAnalyzer
from src.utils.invoker import Invoker


class ParagraphAnalyzer:
    def __init__(self, sentence_analyzer=SentenceAnalyzer()):
        self.sentenceAnalyzer = sentence_analyzer
        self.context = sentence_analyzer.context
        self.invoker = Invoker()

    def analyze(self, paragraph):
        # print "Entering ParagraphAnalyzer.analyze()"
        self.context["sentences"] = []

        for sentence in paragraph.sentences:
            self.invoker.invoke(self.sentenceAnalyzer.analyze, sentence)
            self.context["sentences"].append(sentence)