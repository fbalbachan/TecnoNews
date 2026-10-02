#-*- coding: utf-8 -*-
from src.sentiment.sentiWordNet import SentiWordNet

class ValuatedAdverbFinder:
    def __init__(self, clause):
        self.clause = clause

    def find(self):
        clause = self.clause
        valuated_adverbs = [leaf for leaf in clause.proper_leaves() if leaf.msi["category"] == "adverb"
                                               and leaf.msi["type"] == "general"
                                               and not SentiWordNet.get(leaf.lemma).is_neutral()]
        return valuated_adverbs
