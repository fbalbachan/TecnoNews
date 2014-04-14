# -*- coding: utf-8 -*-

from logging import getLogger

from src.model.clauseAnalyzer import *
from src.model.clauseExtractor import *
from src.parser.freelingTreeParser import *


class FreelingSentenceAnalyzer:
    def __init__(self, tree_parser = FreelingTreeParser()):
        self.tree_parser = tree_parser

    def analyze(self, sentence):
        node = self.tree_parser.from_text(sentence.text)
        sentence.parse_node = node

        self.logger.debug(node.tree_representation())

        sentence.clauses = ClauseExtractor().extract_from(sentence)

        clauseAnalyzer = ClauseAnalyzer()
        for clause in sentence.clauses:
            clauseAnalyzer.analyze(clause)

    logger = getLogger("FreelingSentenceAnalyzer")