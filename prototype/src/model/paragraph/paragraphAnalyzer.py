# -*- coding: utf-8 -*-
from src.model.sentence.sentenceAnalyzer import SentenceAnalyzer
from src.utils.invoker import Invoker

debug_mode = False


class ParagraphAnalyzer:
    def __init__(self, sentence_analyzer=SentenceAnalyzer(), output_demo_debug=False):
        self.sentenceAnalyzer = sentence_analyzer
        self.context = sentence_analyzer.context
        self.invoker = Invoker()
        self.sentenceAnalyzer.output_demo_debug = output_demo_debug

    def analyze(self, paragraph):
        if debug_mode: print "--> ParagraphAnalyzer.analyze()"
        self.context["sentences"] = []

        for sentence in paragraph.sentences:
            self.invoker.invoke(self.sentenceAnalyzer.analyze, sentence)
            self.context["sentences"].append(sentence)