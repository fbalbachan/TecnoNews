#!/usr/bin/python
# -*- coding: utf-8 -*-

class Sentence(object):

    def __init__(self, text):
        self.text = text
        self.parse_node = None
        self.clauses = []

    def main_clause(self):
        root_clauses = filter(lambda clause: clause.is_root(), self.clauses)
        return root_clauses[0]

    def __repr__(self):
        return self.text