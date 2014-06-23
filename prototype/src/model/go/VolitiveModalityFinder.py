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
            if clause.verb.is_modal_of("querer"): return [ GlobalOperator("volitive", clause.verb)]
        return []
