# -*- coding: utf-8 -*-

from src.model.clause.clauseAnalyzer import ClauseAnalyzer
from src.model.clause.clauseExtractor import ClauseExtractor
from src.model.go.globalOperatorAnalyzer import GlobalOperatorAnalyzer
from src.model.sentence.tokenizationGuesser import TokenizationGuesser
from src.parser.freelingTreeParser import FreelingTreeParser
from src.sentiment.sentimentalAnalyzer import SentimentalAnalyzer
from src.utils.invoker import Invoker


class SentenceAnalyzer:
    def __init__(self, tree_parser=FreelingTreeParser()):
        self.tree_parser = tree_parser
        self.context = {"sentences": []}
        self.invoker = Invoker()

    def analyze(self, sentence):
        # print "Entering SentenceAnalyzer.analyze()"
        self.set_parse_tree_to(sentence)
        TokenizationGuesser(sentence).guess()

        sentence.clauses = ClauseExtractor.extract_from(sentence)

        analyze_methods = [self.analyze_clauses_of,
                           SentenceAnalyzer.analyze_global_operators_of,
                           SentenceAnalyzer.analyze_sentimentally]

        for method in analyze_methods:
            self.invoker.invoke(method, sentence)

    @staticmethod
    def analyze_sentimentally(sentence):
        sentimental_analyzer = SentimentalAnalyzer()

        for clause in sentence.clauses:
            sentimental_analyzer.analyze(clause)

    @staticmethod
    def analyze_global_operators_of(sentence):
        GlobalOperatorAnalyzer(sentence).analyze()

    def analyze_clauses_of(self, sentence):
        # print "Entering SentenceAnalyzer.analyze_clauses_of"

        self.context["clauses"] = []
        clause_analyzer = ClauseAnalyzer()
        clause_analyzer.context = self.context

        # print "Clauses: ", sentence.clauses
        for clause in sentence.clauses:
            clause_analyzer.analyze(clause)
            self.context["clauses"].append(clause)

    def set_parse_tree_to(self, sentence):
        node = self.tree_parser.from_text(sentence.text)
        sentence.parse_node = node

        print "TEXT", sentence.text
        print "LEAVES", node.leaves()

        print node.tree_representation()
        for leaf in node.leaves():
            print leaf.original_lexical_form, leaf.lemma, leaf.msi
        print "--------------"
