# -*- coding: utf-8 -*-

class Sentence(object):

    def __init__(self, text):
        self.text = text
        self.parse_node = None
        self.clauses = []

    def main_clause(self):
        return self.clauses_of_level(0)[0]

    def clauses_of_level(self, level):
        return filter(lambda clause: clause.level() == level, self.clauses)

    def non_clause_leaves(self):
        clause_leaves = sum([ clause.node.leaves() for clause in self.clauses_of_level(0) ], [])
        return filter(lambda leaf: leaf not in clause_leaves, self.parse_node.leaves())

    def __repr__(self):
        return self.text