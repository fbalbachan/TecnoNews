# -*- coding: utf-8 -*-

class LexicalForm:
    def __init__(self, lexical_form, msi, lemma, concept):
        self.text = lexical_form
        self.msi = msi
        self.lemma = lemma
        self.concept = concept

    def __repr__(self):
        return self.text + " (" + self.lemma + ") " + repr(self.msi)

    # Duplicado en TacitEntity
    def matches_msi(self, msi):
        for key, value in msi.items():
            if not key in self.msi or self.msi[key] != value: return False
        return True
