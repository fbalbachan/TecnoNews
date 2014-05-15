# -*- coding: utf-8 -*-

from src.ling.tacit_subjects import tacit_subject_for, somebody
from src.model.entity.linkedEntity import LinkedEntity
from src.model.entity.tacitEntity import TacitEntity
from src.model.syntax.syntacticAnalyzer import SyntacticAnalyzer
from src.model.syntax.syntacticStructure import SyntacticStructure


class ActiveVoiceSyntacticAnalyzer(SyntacticAnalyzer):
    def __init__(self, clause):
        SyntacticAnalyzer.__init__(self, clause)

    def subject(self):
        clause = self.clause
        structure = SyntacticStructure("subject")
        if not clause.is_gerund():
            entities = self.verb_matching_subject_entities(3, 2)

            if entities:
                structure.entities = [ entities[0] ]
            else:
                subject = somebody() if clause.is_relative() and clause.is_root() else self.tacit_subject()
                structure.tacit_entities = [ subject ]
        return structure

    def tacit_subject(self):
        verb = self.clause.verb
        return TacitEntity(verb.matching_pronoun(), verb.matching_pronoun_msi())

    def od(self):
        nominal_at_right = lambda: self.search_nominal_od_at("right", 3)
        nominal_at_left  = lambda: self.search_nominal_od_at("left", 2)
        pronominal_at_left  = lambda: self.search_pronoun_at("left", 2)
        pronominal_at_right  = lambda: self.search_pronoun_at("right", 2)
        od = self.extract_searching("od", nominal_at_right, nominal_at_left, pronominal_at_right, pronominal_at_left)

        acusative_pronoun = self.search_duplicated_od_for(od)
        if acusative_pronoun:
            linked_pronoun = LinkedEntity(acusative_pronoun, od.entity())

            self.clause.entities.remove(acusative_pronoun)
            self.clause.linked_entities.append(linked_pronoun)

            od.entities.append(linked_pronoun)
        return od

    def search_duplicated_od_for(self, structure):
        if structure.is_empty(): return
        source_od = structure.entity()
        entities = self.clause.entities_closest_to_verb(("left", 3), ("right", 2))
        acusative_pronouns = self.only_acusative_pronouns_of(entities)
        matching_pronouns = filter(lambda pronoun: source_od.matches(pronoun), acusative_pronouns)

        if len(matching_pronouns) > 1: raise Exception("Se encontró más de un pronombre duplicando el OD.")

        if matching_pronouns:
            pronoun = matching_pronouns[0]
            return pronoun if pronoun != source_od else None
        return None

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
        entities = self.valid_subject_entities(2, 3) + \
            self.search_subord_with_preposition_at("right", 3, "de", "para")
        if entities: structure.entities = [ entities[0] ]
        return structure

    def search_regime_at(self, side, distance):
        return self.search_subord_with_preposition_at(side, distance)

    def search_nominal_oi_at(self, side, distance):
        return self.search_subord_with_preposition_at(side, distance, "a")

    def search_nominal_od_at(self, side, distance):
        non_subord_method = lambda side, distance: \
            self.only_nominal_of(self.clause.entities_closest_to_verb_at(side, distance))
        subord_method = lambda side, distance: self.search_subord_with_preposition_at(side, distance, "a")
        search_methods = [ non_subord_method, subord_method ]

        for method in search_methods:
            entities = method(side, distance)
            if entities:
                return [ entities[0] ]
        return []