#-*- coding: utf-8 -*-
import ConfigParser

from src.model.go.globalOperator import GlobalOperator


def load_volitive_verbs():
    Config = ConfigParser.ConfigParser()
    Config.read("config")
    resources_file = dict(Config.items("resources"))["general_resources"]

    Config.read(resources_file)
    string = dict(Config.items("go"))["volitive_verbs"]
    verbs = set()
    for verb in string.split(","):
        verbs.add(verb.strip())
    return verbs

class VolitiveModalityFinder:

    def __init__(self, clause):
        self.clause = clause

    def find(self):
        operators = []
        methods = [ self.find_subordinated, self.find_selected_verbs, self.find_selected_words ]
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

    def find_subordinated(self):
        clause = self.clause
        if clause.is_subordinated_with("que") and clause.father.voice:
            father_verb_lemma = clause.father.verb.lemma()
            if father_verb_lemma in self.volitive_verbs:
                return [ GlobalOperator("volitive", father_verb_lemma + " + subord 'que' (CS)")]
        return []

    volitive_verbs = load_volitive_verbs()