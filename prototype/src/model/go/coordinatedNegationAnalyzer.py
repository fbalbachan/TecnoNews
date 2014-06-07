# -*- coding: utf-8 -*-
from src.model.go.globalOperator import GlobalOperator

class CoordinatedNegationAnalyzer:

    def __init__(self, sentence):
        self.sentence = sentence

    def analyze(self):
        sentence = self.sentence
        negation_lemmas = [ "ni" ]
        leaves = filter(lambda leaf: leaf.lemma in negation_lemmas, sentence.non_clause_leaves())

        if leaves:
            sentence_leaves = sentence.parse_node.leaves()
            leaf = leaves[0]
            leaf_index = sentence_leaves.index(leaf)
            affected_clauses = filter(lambda clause: leaf_index < sentence_leaves.index(clause.node.leaves()[0]),
                                      sentence.clauses_of_level(0))

            affected_clauses = sum([ list(clause) for clause in affected_clauses ], [])
            for clause in affected_clauses:
                operator = GlobalOperator("negation", leaf)
                clause.global_operators.add(operator)