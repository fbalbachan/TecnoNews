#!/usr/bin/python
# -*- coding: utf-8 -*-

class Sentiment(object):
    def __init__(self, (pos, neg)=(0.0, 0.0)):
        self.pos = pos
        self.neg = neg

    def add(self, (pos, neg)):
        self.pos += pos
        self.neg += neg

    def get(self):
        return (self.pos, self.neg)
