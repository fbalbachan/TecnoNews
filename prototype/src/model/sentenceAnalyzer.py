# -*- coding: utf-8 -*-

from logging import getLogger

from src.model.clauseAnalyzer import ClauseAnalyzer
from src.model.clauseExtractor import ClauseExtractor
from src.parser.freelingTreeParser import FreelingTreeParser


class SentenceAnalyzer:
    def __init__(self, tree_parser = FreelingTreeParser()):
        self.tree_parser = tree_parser
        self.context = {}

    def analyze(self, sentence):
        self.set_parse_tree_to(sentence)

        sentence.clauses = ClauseExtractor().extract_from(sentence)

        self.context["clauses"] = []
        clauseAnalyzer = ClauseAnalyzer()
        clauseAnalyzer.context = self.context
        for clause in sentence.clauses:
            clauseAnalyzer.analyze(clause)
            self.context["clauses"].append(clause)

    def set_parse_tree_to(self, sentence):
        node = self.tree_parser.from_text(sentence.text)
        sentence.parse_node = node
        print node.tree_representation()
        self.logger.debug(node.tree_representation())

    logger = getLogger("SentenceAnalyzer")