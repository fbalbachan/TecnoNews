#!/usr/bin/python
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

    def __repr__(self):
        return self.text