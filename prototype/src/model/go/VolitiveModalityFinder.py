#-*- coding: utf-8 -*-
import ConfigParser

from src.model.go.globalOperator import GlobalOperator
from src.utils import resources


class VolitiveModalityFinder:

    def __init__(self, clause):
        self.clause = clause

    def find(self):
        operators = []
        methods = [ self.find_selected_verbs, self.find_selected_words ]
        for method in methods: operators.extend(method())
        return operators

    def find_selected_words(self):
        clause = self.clause

        lemmas = [ "ojalá" ]
        leaves = filter(lambda leaf: leaf.lemma in lemmas, clause.proper_leaves())
        return [ GlobalOperator("volitive", leaf) for leaf in leaves ]

    def find_selected_verbs(self):
        clause = self.clause
        if clause.voice:
            leaf = clause.verb.leaves[0]
            if leaf.lemma == "querer" and clause.verb.is_compound():
                return [ GlobalOperator("volitive", clause.verb)]
        return []
