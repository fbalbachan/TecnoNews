# -*- coding: utf-8 -*-

from src.ling.tacit_subjects import tacit_subject_for
from src.model.syntacticAnalyzer import SyntacticAnalyzer
from src.model.syntacticStructure import SyntacticStructure
from src.model.tacitEntity import TacitEntity


class ActiveVoiceSyntacticAnalyzer(SyntacticAnalyzer):
    def __init__(self, clause):
        SyntacticAnalyzer.__init__(self, clause)

    def subject(self):
        structure = SyntacticStructure("subject")
        entities = self.nominal_and_personal_entities(3, 2)

        if entities:
            structure.entities = [ entities[0] ]
        else:
            structure.tacit_entities = [ self.tacit_subject() ]

        return structure

    def tacit_subject(self):
        verb = self.clause.verb
        return TacitEntity(verb.matching_pronoun(), verb.matching_pronoun_msi())

    def od(self):
        nominal_at_right = lambda: self.search_nominal_od_at("right", 3)
        nominal_at_left  = lambda: self.search_nominal_od_at("left", 2)
        pronominal_at_left  = lambda: self.search_pronoun_at("left", 2)
        pronominal_at_right  = lambda: self.search_pronoun_at("right", 2) # Enclítico
        return self.extract_searching("od", nominal_at_right, nominal_at_left, pronominal_at_left, pronominal_at_right)

    def oi(self):
        nominal_at_right = lambda: self.search_nominal_oi_at("right", 3)
        nominal_at_left  = lambda: self.search_nominal_oi_at("left", 3)
        pronominal_at_left  = lambda: self.search_pronoun_at("left", 2)
        pronominal_at_right  = lambda: self.search_pronoun_at("right", 2)
        return self.extract_searching("oi", nominal_at_right, nominal_at_left, pronominal_at_left, pronominal_at_right)

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
        return self.search_subord_with_preposition_at(side, distance, "a", "con", "de")

    def search_nominal_oi_at(self, side, distance):
        return self.search_subord_with_preposition_at(side, distance, "a")

    def search_nominal_od_at(self, side, distance):
        clause = self.clause
        entities = self.only_nominal(clause.entities_closest_to_verb_at(side, distance))
        if entities:
            return [ entities[0] ]
        else:
            return self.search_subord_with_preposition_at(side, distance, "a")