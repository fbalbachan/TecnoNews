#!/usr/bin/python
# -*- coding: utf-8 -*-

class Sentence(object):

    def __init__(self, text):
        self.text = text
        self.parse_node = None
        self.clauses = []

    def __repr__(self):
        return self.text