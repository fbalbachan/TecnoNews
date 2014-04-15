# -*- coding: utf-8 -*-

class SyntacticStructure:
    def __init__(self, name):
        self.name = name
        self.entities = []
        self.tacit_entities = []

    def lexical_form(self):
        return self.entity().lexical_form

    def entity(self):
        return (self.entities + self.tacit_entities)[0]

    def is_tacit(self):
        return not bool(self.entities) and bool(self.tacit_entities)

    def __repr__(self):
        entities = self.entities + self.tacit_entities
        return str(entities[0] if len(entities) == 1 else entities)