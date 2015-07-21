#-*- coding: utf-8 -*-
from src.sentiment.sentiWordNet import SentiWordNet

class ValuatedAdverbFinder:
    def __init__(self, clause):
        self.clause = clause

    def find(self):
        clause = self.clause
        valuated_adverbs = filter(lambda leaf: leaf.msi["category"] == "adverb"
                                               and leaf.msi["type"] == "general"
                                               and not SentiWordNet.get(leaf.lemma).is_neutral(),
                                  clause.proper_leaves())
        return valuated_adverbs
