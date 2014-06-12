#-*- coding: utf-8 -*-
from src.model.go.globalOperator import GlobalOperator
from src.utils import resources


def load_verbs():
    verbs = {}
    rsrc = resources.instance
    for klass in GlobalOperator.classes:
        key = klass + "_verbs"
        if rsrc.has_key("go", key):
            verb_list = rsrc.parse_csv_in("go", key)
            for verb in verb_list:
                if verb in verbs:
                    verbs[verb].append(klass)
                else:
                    verbs[verb] = [ klass ]
    return verbs

class VerbsWithSubordinatedFinder():
    def __init__(self, clause):
        self.clause = clause

    def find(self):
        operators = []
        clause = self.clause
        if clause.is_subordinated_with("que") and clause.father.voice:
            father_verb_lemma = clause.father.verb.lemma()
            if father_verb_lemma in self.verbs:
                for klass in self.verbs[father_verb_lemma]:
                    operators.append(GlobalOperator(klass, father_verb_lemma + " + subord 'que' (CS)"))
        return operators

    verbs = load_verbs()