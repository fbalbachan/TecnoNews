# -*- coding: utf-8 -*-

from copy import copy
from itertools import groupby

from src.ling.head_labels import *
from src.ling.tacit_subjects import tacit_subjects
from src.ling.verb_info import get_script_class, get_transitivity
from src.model.entity import Entity


# Que el verbo sea una entidad es una licencia como también que exista una función sintáctica superior "verbo".
class Verb(Entity):

    def __init__(self, node, voice, leaves):
        Entity.__init__(self, node)

        self.voice = voice
        self.leaves = leaves

        lemma = self.lemma()
        self.msi = self.guess_msi()
        self.lexical_form = " ".join([ str(leaf) for leaf in self.leaves])

        self.script_class = get_script_class(lemma) # Reificar como método de clase
        self.transitivity = get_transitivity(lemma) # Idem

        if not self.transitivity:
            raise Exception("No se encontró información de transitividad para " + self.leaf().lexical_form)

    def lemma(self):
        return self.leaf().lemma

    def leaf(self):
        return self.leaves[-1]

    def is_compound(self):
        return len(self.leaves) > 1

    def matches(self, entity):
        matches = self.msi["number"] == entity.msi["number"] and self.msi["person"] == entity.msi["person"] and \
            self.matches_gender_of(entity)
        return matches

    def matches_gender_of(self, entity):
        msi = self.msi
        return msi["gender"] == "neutral" or entity.msi["gender"] == "neutral" or msi["gender"] == entity.msi["gender"]

    def guess_msi(self):
        first_leaf = self.leaves[0]

        person = first_leaf.msi["person"]
        gender = "neutral" if self.voice == "active" else (self.leaf().msi["gender"] or "neutral")
        number = first_leaf.msi["number"]
        mode = first_leaf.msi["mode"]

        return { "category" : "verb", "gender" : gender, "number" : number, "person" : person, "mode" : mode }

    def matching_pronoun(self):
        neutral_pronouns = { (1, "singular"), (2, "singular"), (2, "plural") }

        msi = self.msi
        person = msi["person"]
        number = msi["number"]
        gender = "neutral" if (person, number) in neutral_pronouns else msi["gender"]
        return tacit_subjects[(person, number, gender)]

    def matching_pronoun_msi(self):
        msi = self.msi
        return { "category" : "pronoun", "person" : msi["person"], "number" : msi["number"], "gender" : msi["gender"] }

    def __repr__(self):
        return " ".join([ str(leaf) for leaf in self.leaves]) + " (" + self.lemma() + ") " + \
            str([ self.voice, self.script_class, self.transitivity ]) + str(self.msi)
