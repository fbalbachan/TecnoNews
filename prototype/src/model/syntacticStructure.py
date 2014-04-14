# -*- coding: utf-8 -*-

class SyntacticStructure:
    def __init__(self, name):
        self.name = name
        self.entities = []

    def entity(self):
        return self.entities[0]

    def __repr__(self):
        return str(self.entities[0] if len(self.entities) == 1 else self.entities)
