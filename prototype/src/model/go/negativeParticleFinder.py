# -*- coding: utf-8 -*-
from src.model.go.globalOperator import GlobalOperator

class NegativeParticleFinder:

    def __init__(self, clause):
        self.clause = clause

    def find(self):
        clause = self.clause

        negation_lemmas = [ "nunca", "nadie", "nada", "jamás", "tampoco", "ninguno", "ni" ]
        negation_lexical_forms = [ "difícilmente" ]

        leaves = filter(lambda leaf: leaf.lemma in negation_lemmas or leaf.lexical_form in negation_lexical_forms,
                        clause.proper_leaves())

        no_leaf = self.find_no_negation_leaf()
        if no_leaf: leaves.append(no_leaf)

        return [ GlobalOperator("negation", leaf) for leaf in leaves ]

    def find_no_negation_leaf(self):
        clause = self.clause
        if not clause.voice: return

        leaves = clause.proper_leaves()
        verb_index = leaves.index(clause.verb.leaves()[0])

        no_leaves = filter(lambda leaf: leaf.lemma == "no" and leaves.index(leaf) < verb_index, leaves)
        if not no_leaves: return

        no_leaf = no_leaves[0]
        middle_leaves = leaves[leaves.index(no_leaf)+1:verb_index]
        if all([ leaf.msi["category"] == "pronoun" for leaf in middle_leaves ]): return no_leaf