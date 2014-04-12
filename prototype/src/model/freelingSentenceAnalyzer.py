# -*- coding: utf-8 -*-

from src.model.clauseAnalyzer import *
from src.model.clauseExtractor import *
from src.parser.freelingTreeParser import *


class FreelingSentenceAnalyzer:
    def analyze(self, sentence):
        tree_parser = FreelingTreeParser()
        node = tree_parser.from_text(sentence.text)
        sentence.parse_node = node

        print node.tree_representation()

        sentence.clauses = ClauseExtractor().extract_from(sentence)

        clauseAnalyzer = ClauseAnalyzer()
        for clause in sentence.clauses:
            clauseAnalyzer.analyze(clause)
