# -*- coding: utf-8 -*-

class Token:
    def __init__(self):
        self.components = []

    def start(self):
        return self.components[0][0]

    def end(self):
        return self.components[-1][1]

    def __repr__(self):
        return "(" + str(self.start()) + ", " + str(self.end()) + ")"