# -*- coding: utf-8 -*-

class Concept:
    def __init__(self, name):
        self.name = name
        self.lexical_forms = []

    def add(self, lexical_form):
        self.lexical_forms.append(lexical_form)
        lexical_form.concept = self

    def __repr__(self):
        return "Concept " + self.name