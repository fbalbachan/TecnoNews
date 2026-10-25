# -*- coding: utf-8 -*-
from src.ontology.concept import Concept

class Ontology:
    def __init__(self, name):
        self.name = name
        self.concepts = {}

    def add(self, concept):
        self.concepts[concept.name] = concept

    def concept(self, name, create_if_necessary=False):
        if name not in self.concepts and create_if_necessary:
            self.concepts[name] = Concept(name)
        return self.concepts[name]

    def get_lexical_forms(self, lemma, msi):
        return self._get_lexical_forms(lemma, msi)

    def get_lexical_form(self, lemma, msi):
        lexical_forms = self._get_lexical_forms(lemma, msi, True)
        return lexical_forms[0] if lexical_forms else None

    def get_lemma_and_msi(self, a_lexical_form):
        for concept in list(self.concepts.values()):
            for lexical_form in concept.lexical_forms:
                if lexical_form.text == a_lexical_form:
                    return {"lemma": lexical_form.lemma, "msi": lexical_form.msi}

    def _get_lexical_forms(self, lemma, msi, stop_on_match=False):
        lexical_forms = []
        for concept in list(self.concepts.values()):
            for lexical_form in concept.lexical_forms:
                if lexical_form.lemma == lemma and lexical_form.matches_msi(msi):
                    if stop_on_match:
                        return [lexical_form]
                    lexical_forms.append(lexical_form)
        return lexical_forms

    def is_valid_word(self, word):
        for concept in list(self.concepts.values()):
            for lexical_form in concept.lexical_forms:
                if lexical_form.text == word:
                    return True
        return False
