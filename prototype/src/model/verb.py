# -*- coding: utf-8 -*-

from itertools import groupby

from entity import *
from ling.head_labels import *
from ling.verb_info import get_script_class, get_transitivity


# Que el verbo sea una entidad es una licencia como también que exista una función sintáctica superior "verbo".
class Verb(Entity):

    def __init__(self, node, voice):
        Entity.__init__(self, node)

        lemma = self.lemma()
        self.msi = self.leaf().msi

        self.voice = voice
        self.script_class = get_script_class(lemma) # Reificar como método de clase
        self.transitivity = get_transitivity(lemma) # Idem

    def lemma(self):
        return self.leaf().lemma

    def leaf(self):
        return self.node.nodes_with_labels(["parti"])[0].leaves()[0] if self.is_compound() else self.node.leaves()[0]

    def is_compound(self):
        return bool(self.node.nodes_with_labels(["vaux"]))

    def matches(self, entity):
        person_entity = entity.msi["person"] if "person" in entity.msi else 3
        return self.msi["number"] == entity.msi["number"] and self.msi["person"] == person_entity

    def __repr__(self):
        node = self.leaf()
        return node.lexical_form + " (" + node.lemma + ") " + str([ self.voice, self.script_class, self.transitivity ])