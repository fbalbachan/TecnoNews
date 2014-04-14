# -*- coding: utf-8 -*-

from copy import copy
from itertools import groupby

from src.ling.head_labels import *
from src.ling.verb_info import get_script_class, get_transitivity
from src.model.entity import Entity


# Que el verbo sea una entidad es una licencia como también que exista una función sintáctica superior "verbo".
class Verb(Entity):

    def __init__(self, node, voice):
        Entity.__init__(self, node)

        self.voice = voice

        lemma = self.lemma()
        self.msi = self.adjusted_msi()

        self.script_class = get_script_class(lemma) # Reificar como método de clase
        self.transitivity = get_transitivity(lemma) # Idem

        if not self.transitivity:
            raise Exception("No se encontró información de transitividad para " + self.leaf().lexical_form)

    def lemma(self):
        return self.leaf().lemma

    def leaf(self):
        return self.verbal_leaves()[-1]

    def is_compound(self):
        return len(self.verbal_leaves()) > 1

    def verbal_leaves(self):
        return self.node.leaves_of_category("verb")

    def matches(self, entity):
        person_of_entity = entity.msi["person"] if "person" in entity.msi else 3
        matches = self.msi["number"] == entity.msi["number"] and self.msi["person"] == person_of_entity
        if self.voice == "passive": matches = matches and self.matches_gender_of(entity)
        return matches

    def matches_gender_of(self, entity):
        return self.msi["gender"] == entity.msi["gender"] or entity.msi["gender"] == "neutral"

    def adjusted_msi(self):
        verb_index_for_msi = -1 if self.voice == "passive" else 0 # Active
        adjusted = copy(self.verbal_leaves()[verb_index_for_msi].msi)
        if not adjusted["person"]: adjusted["person"] = 3
        return adjusted

    def __repr__(self):
        return self.node.leaves_string() + " (" + self.lemma() + ") " + \
            str([ self.voice, self.script_class, self.transitivity ]) + str(self.msi)
