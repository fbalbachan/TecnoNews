# -*- coding: utf-8 -*-
from src.model.go.globalOperator import GlobalOperator

class ConditionFinder:
    def __init__(self, clause):
        self.clause = clause

    def find(self):
        if not self.clause.has_global_operator_of("question"):
            methods = [ self.find_conditional_si, self.find_en_caso_de_que_or_siempre_y_cuando ]
            return sum([ method() for method in methods ], [])
        else:
            return []

    def find_en_caso_de_que_or_siempre_y_cuando(self):
        operators = []
        clause = self.clause
        leaves = clause.proper_leaves()
        #at_left = [ leaf.lexical_form for leaf in clause.leaves_at_left()[-1:] ]
        #if leaves[0].lexical_form == "que":
        #    if at_left == ["en_caso_de"]: operators.append(GlobalOperator("condition", at_left[0]))
        #else:
        #    if at_left == ["siempre_y_cuando"]: operators.append(GlobalOperator("condition", at_left[0]))

        if leaves[0].lexical_form == "en_caso_de_que":
            operators.append(GlobalOperator("condition", "en_caso_de_que"))
        elif leaves[0].lexical_form == "siempre_y_cuando":
            operators.append(GlobalOperator("condition", "siempre_y_cuando"))

        return operators

    def find_conditional_si(self):
        leaves = filter(self.is_si_conditional, self.clause.proper_leaves())
        return [ GlobalOperator("condition", leaf) for leaf in leaves ]

    def is_si_conditional(self, leaf):
        check_by_lemma = { "si": lambda l: l.msi["category"] == "conjunction" and l.msi["type"] == "subordinated" }
        lemma = leaf.lemma
        return lemma in check_by_lemma.keys() and check_by_lemma[lemma](leaf)
