# -*- coding: utf-8 -*-

class Rewrite:
    def __init__(self, node, replacement):
        self.node = node
        self.replacement = replacement

    def token(self):
        return self.node.token

    def __repr__(self):
        return self.node.leaves_string() + " -> " + self.replacement