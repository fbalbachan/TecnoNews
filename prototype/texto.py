#!/usr/bin/python
# -*- coding: utf-8 -*-

class Texto(object):
    def __init__(self):
        self.sentences = []
        
    def add(self, sentence):
        self.sentences.append(sentence)

    def __repr__(self):
        return "%d sentences, %d clauses" % (len(self.sentences), sum([len(s.clauses) for s in self.sentences]))
