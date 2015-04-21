# -*- coding: utf-8 -*-

from src.ling.tacit_subjects import this, get_entity_some
from src.model.entity.tacitEntity import TacitEntity
from src.model.syntax.syntacticAnalyzer import SyntacticAnalyzer
from src.model.entity.entity import Entity
from src.model.entity.animityEnum import AnimityEnum


class ActiveVoiceSyntacticAnalyzer(SyntacticAnalyzer):
    def __init__(self, clause):
        SyntacticAnalyzer.__init__(self, clause)

    def subject(self):
        # print "Entering ActiveVoiceSyntacticAnalyzer.subject()"

        clause = self.clause
        if clause.is_gerund():
            subject = []
            return subject

        verbal_animity = clause.verb.subject_animity
        entities = self.verb_matching_subject_entities(4, 3)
        entities = self.filter_by_animity(entities, verbal_animity)

        if entities:
            entities[0].msi["animity"] = AnimityEnum.most_specific(verbal_animity, entities[0].msi["animity"])
            subject = [entities[0]]

        else:
            subject = [self.tacit_or_implicit_subject(verbal_animity)]

        return subject

    def tacit_or_implicit_subject(self, verbal_animity=AnimityEnum.bianimate):
        # print "Subject is tacit or implicit"

        if self.is_root_relative_clause():
            is_implicit = True
            entity_some = get_entity_some(verbal_animity, is_implicit)
            return entity_some

        if self.clause.has_kind_of_cataphoric_structure():
            return this()

        return self.tacit_subject(verbal_animity)

    def is_root_relative_clause(self):
        clause = self.clause
        return clause.is_relative() and clause.is_root()

    def tacit_subject(self, verbal_animity=AnimityEnum.bianimate):
        verb = self.clause.verb
        pronoun = verb.matching_pronoun()
        pronoun_msi = verb.matching_pronoun_msi()
        pronoun_msi['animity'] = AnimityEnum.animated if pronoun_msi['person'] in [1, 2] else verbal_animity

        return TacitEntity(pronoun, pronoun_msi)

    def od(self):
        # print "Entering ActiveVoiceSyntacticAnalyzer.od()"
        verbal_animity = self.clause.verb.affected_object_animity

        nominal_entities_at_same_level_nodes = \
                self.find_entities_by(lambda: self.search_nominal_od_at_same_level_nodes("right", 3, verbal_animity),
                                      lambda: self.search_nominal_od_at_same_level_nodes("left", 2, verbal_animity))

        nominal_entities_under_prep_a = \
                self.find_entities_by(lambda: self.search_nominal_od_under_prep_a("right", 4),
                                      lambda: self.search_nominal_od_under_prep_a("left", 3))

        pronominal_entities = \
                self.find_entities_by(lambda: self.search_pronoun_at("right", 3, verbal_animity),
                                      lambda: self.search_pronoun_at("left", 3, verbal_animity))

        candidate_entities_matching_anim = nominal_entities_at_same_level_nodes \
                                           + self.filter_by_animity(nominal_entities_under_prep_a, verbal_animity) \
                                           + pronominal_entities

        candidate_entities = nominal_entities_at_same_level_nodes \
                             + nominal_entities_under_prep_a \
                             + pronominal_entities

        if not candidate_entities:
            is_implicit = True
            return [get_entity_some(verbal_animity, is_implicit)]

        if candidate_entities[0].is_subordinated_with_preposition("a"):
            linked = self.link_duplicated_od_for(candidate_entities)
            if linked:
                return [candidate_entities[0], linked]
            else:
                if not candidate_entities_matching_anim:
                    is_implicit = True
                    return [get_entity_some(verbal_animity, is_implicit)]

                return [candidate_entities_matching_anim[0]]
        else:
            return [candidate_entities[0]]

    def link_duplicated_od_for(self, od_candidates):
        accusative_pronoun = self.search_duplicated_od_for(od_candidates[0])
        if accusative_pronoun:
            accusative_pronoun.add_coreference(od_candidates[0])
            od_candidates.append(accusative_pronoun)

        return accusative_pronoun

    def search_duplicated_od_for(self, source_od):

        closest_entities = self.clause.entities_closest_to_verb(("left", 3), ("right", 2))
        accusative_pronouns = self.only_accusative_pronouns_of(closest_entities)
        matching_pronouns = filter(lambda pronoun: source_od.matches(pronoun),
                                   accusative_pronouns)

        if len(matching_pronouns) > 1:
            raise Exception("Se encontró más de un pronombre duplicando el OD.")

        if not matching_pronouns:
            return None

        result = matching_pronouns[0] if matching_pronouns[0] != source_od else None

        return result

    def oi(self):
        # print "Entering ActiveVoiceSyntacticAnalyzer.oi()"
        entities = self.find_entities_by(lambda: self.search_nominal_oi_at("right", 3, AnimityEnum.animated),
                                         lambda: self.search_nominal_oi_at("left", 3, AnimityEnum.animated),
                                         lambda: self.search_pronoun_at("left", 2, AnimityEnum.animated),
                                         lambda: self.search_pronoun_at("right", 2, AnimityEnum.animated))
        if entities:
            entities[0].msi["animity"] = AnimityEnum.most_specific(entities[0].msi["animity"], AnimityEnum.animated)
        candidates = [entities[0]] if entities else []
        return candidates

    def regimen(self):
        # print "Entering ActiveVoiceSyntacticAnalyzer.regimen()"
        verbal_animity = self.clause.verb.affected_object_animity
        entities = self.get_regimen_candidate_entities(verbal_animity)
        if entities:
            entities[0].msi["animity"] = AnimityEnum.most_specific(entities[0].msi["animity"], verbal_animity)
        candidates = [entities[0]] if entities else []
        return candidates

    def get_regimen_candidate_entities(self, verbal_animity):
        at_right = lambda: self.search_regime_at("right", 3, verbal_animity)
        at_left = lambda: self.search_regime_at("left", 2, verbal_animity)
        entities = self.find_entities_by(at_right, at_left)
        return entities

    def search_regime_at(self, side, distance, verbal_animity):
        entities = self.search_subords_with_prep_at(side, distance, "a", "por", "en", "de", "contra", "con", "sobre")
        entities = self.filter_by_animity(entities, verbal_animity)
        candidates = [entities[0]] if entities else []
        return candidates

    def equative(self):
        # print "Entering ActiveVoiceSyntacticAnalyzer.equative()"
        verbal_animity = self.clause.verb.affected_object_animity
        entities = self.get_equative_candidate_entities(verbal_animity)
        if entities:
            entities[0].msi["animity"] = AnimityEnum.most_specific(entities[0].msi["animity"], verbal_animity)
        candidates = [entities[0]] if entities else []
        return candidates

    def get_equative_candidate_entities(self, verbal_animity):
        entities = self.valid_subject_entities(2, 3) \
                  + self.search_subords_with_prep_at("right", 3, "de", "para")
        entities = self.filter_by_animity(entities, verbal_animity)
        return entities

    def search_nominal_oi_at(self, side, distance, animity=AnimityEnum.bianimate):
        entities = self.search_subords_with_prep_at(side, distance, "a", "para")
        entities = Entity.only_maximal(entities)
        entities = self.filter_infinitives(entities)
        entities = self.filter_by_animity(entities, animity)
        return entities

    def search_nominal_od_at_same_level_nodes(self, side, distance, verbal_animity=AnimityEnum.bianimate):
        entities = self.clause.entities_closest_to_verb_at(side, distance)
        entities = self.only_nominal_of(entities)
        entities = self.filter_by_animity(entities, verbal_animity)
        return entities

    def search_nominal_od_under_prep_a(self, side, distance, verbal_animity=AnimityEnum.bianimate):
        entities = self.search_subords_with_prep_at(side, distance, "a")
        entities = Entity.only_maximal(entities)
        entities = self.filter_infinitives(entities)
        entities = self.filter_by_animity(entities, verbal_animity)
        return entities
