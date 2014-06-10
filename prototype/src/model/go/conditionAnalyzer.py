# -*- coding: utf-8 -*-
from src.model.go.globalOperator import GlobalOperator

class ConditionAnalyzer:
    def __init__(self, sentence):
        self.sentence = sentence

    def analyze(self):
        sentence = self.sentence
        leaves = filter(self.is_condition_word, sentence.parse_node.leaves())
        operators = [ GlobalOperator("condition", leaf) for leaf in leaves ]
        for clause in sentence.clauses: clause.global_operators.update(operators)

    def is_condition_word(self, leaf):
        def check_en_caso_de(l):
            leaves = self.sentence.parse_node.leaves()
            leaves = leaves[leaves.index(l) + 1:leaves.index(l) + 2]
            return [ each.lexical_form for each in leaves ] == ["que"]

        check_by_lemma = { "si": lambda l: l.msi["category"] == "conjunction" and l.msi["type"] == "subordinated",
                          "en_caso_de": check_en_caso_de,
                          "siempre_y_cuando": lambda leaf: True }
        lemma = leaf.lemma
        return lemma in check_by_lemma.keys() and check_by_lemma[lemma](leaf)