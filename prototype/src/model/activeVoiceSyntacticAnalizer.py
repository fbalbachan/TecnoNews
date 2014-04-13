# -*- coding: utf-8 -*-

from src.ling.tacit_subjects import tacit_subject_for
from src.model.subject import Subject
from src.model.syntacticAnalyzer import SyntacticAnalyzer
from src.model.syntacticStructure import SyntacticStructure


class ActiveVoiceSyntacticAnalyzer(SyntacticAnalyzer):
    def __init__(self, clause):
        SyntacticAnalyzer.__init__(self, clause)

    def subject(self):
        entities = self.nominal_and_personal_entities(3, 2)
        if entities: return Subject.concrete(entities[0])
        return self.tacit_subject()

    def tacit_subject(self):
        verb = self.clause.verb
        tacit_msi = { "person" : verb.msi["person"], "number" : verb.msi["number"], "gender" : verb.msi["gender"] }
        return Subject.tacit(tacit_subject_for(verb), tacit_msi)

    def od(self):
        nominal_at_right = lambda: self.search_nominal_od_at("right", 3)
        nominal_at_left  = lambda: self.search_nominal_od_at("left", 2)
        pronominal_at_left  = lambda: self.search_pronoun_at("left", 1)
        pronominal_at_right  = lambda: self.search_pronoun_at("right", 1) # Enclítico
        return self.extract_searching("od", nominal_at_right, nominal_at_left, pronominal_at_left, pronominal_at_right)

    def oi(self):
        nominal_at_right = lambda: self.search_nominal_oi_at("right", 3)
        nominal_at_left  = lambda: self.search_nominal_oi_at("left", 3)
        pronominal_at_left  = lambda: self.search_pronoun_at("left", 1)
        return self.extract_searching("oi", nominal_at_right, nominal_at_left, pronominal_at_left)

    def regimen(self):
        at_right = lambda: self.search_regime_at("right", 3)
        at_left  = lambda: self.search_regime_at("left", 2)
        return self.extract_searching("regimen", at_right, at_left)

    def equative(self):
        structure = SyntacticStructure("equative")
        entities = self.nominal_and_personal_entities(2, 3)
        if entities: structure.entities = [ entities[0] ]
        return structure

    def search_regime_at(self, side, distance):
        def which(node):
            first_leaf = node.leaves()[0]
            return first_leaf.msi["type"] == "preposition" and first_leaf.lexical_form.lower() in ["a", "con", "de"]
        return self.search_subord_at(side, distance, which)

    def search_nominal_oi_at(self, side, distance):
        def which(node):
            first_leaf = node.leaves()[0]
            return first_leaf.msi["type"] == "preposition" and first_leaf.lexical_form.lower() == "a"
        return self.search_subord_at(side, distance, which)

    def search_nominal_od_at(self, side, distance):
        clause = self.clause
        entities = self.only_nominal(clause.entities_closest_to_verb_at(side, distance))
        if entities:
            return [ entities[0] ]
        else:
            return self.search_subord_at(side, distance)