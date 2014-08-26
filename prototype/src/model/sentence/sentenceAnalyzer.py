# -*- coding: utf-8 -*-

from src.model.clause.clauseAnalyzer import ClauseAnalyzer
from src.model.clause.clauseExtractor import ClauseExtractor
from src.model.go.globalOperatorAnalyzer import GlobalOperatorAnalyzer
from src.model.sentence.tokenizationGuesser import TokenizationGuesser
from src.parser.freelingTreeParser import FreelingTreeParser
from src.sentiment.sentimentalAnalyzer import SentimentalAnalyzer
from src.sentiment.sentimentalSummarizer import SentimentalSummarizer
from src.utils.invoker import Invoker


class SentenceAnalyzer:
    def __init__(self, tree_parser = FreelingTreeParser()):
        self.tree_parser = tree_parser
        self.context = { "sentences" : [] }
        self.invoker = Invoker()

    def analyze(self, sentence):
        self.set_parse_tree_to(sentence)
        TokenizationGuesser(sentence).guess()

        return
        sentence.clauses = ClauseExtractor().extract_from(sentence)
        for method in [ self.analyze_clauses_of, self.analyze_global_operators_of, self.analyze_sentimentally ]:
            self.invoker.invoke(method, sentence)

    def analyze_sentimentally(self, sentence):
        sentimentalAnalyzer =  SentimentalAnalyzer()

        for clause in sentence.clauses:
            sentimentalAnalyzer.analyze(clause)

    def analyze_global_operators_of(self, sentence):
        GlobalOperatorAnalyzer(sentence).analyze()

    def analyze_clauses_of(self, sentence):
        self.context["clauses"] = []
        clauseAnalyzer = ClauseAnalyzer()
        clauseAnalyzer.context = self.context
        for clause in sentence.clauses:
            clauseAnalyzer.analyze(clause)
            self.context["clauses"].append(clause)

    def set_parse_tree_to(self, sentence):
        node = self.tree_parser.from_text(sentence.text)
        sentence.parse_node = node

        #print node.tree_representation()
        #for leaf in node.leaves():  print leaf.original_lexical_form, leaf.lemma, leaf.msi
        #print "--"