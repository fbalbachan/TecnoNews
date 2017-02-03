# -*- coding: utf-8 -*-
from src.model.tokenization.token import Token


class Sentence(object):
    # TODO: Repensar parámetros: text o paragraph? o ambos?
    def __init__(self, text, paragraph=None):
        self.text = text
        self.paragraph = paragraph
        self.token = self.build_token()
        self.parse_node = None
        self.clauses = []
        self.rewritable = True

    def main_clause(self):
        # TODO: Preguntarle a Lean por qué toma [0] si dijo que puede haber más de una
        return self.clauses_of_level(0)[0]

    def main_clauses(self):
        return self.clauses_of_level(0)

    def clauses_of_level(self, level):
        return filter(lambda clause: clause.level() == level, self.clauses)

    def non_clause_leaves(self):
        clause_leaves = sum([ clause.node.leaves() for clause in self.clauses_of_level(0) ], [])
        return filter(lambda leaf: leaf not in clause_leaves, self.parse_node.leaves())

    def __repr__(self):
        return self.text

    def build_token(self):
        token = Token()
        token.append(0, len(self.text))
        return token
