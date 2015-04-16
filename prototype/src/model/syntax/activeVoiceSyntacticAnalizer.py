# -*- coding: utf-8 -*-

from src.ling.tacit_subjects import implicit_somebody, this, get_entity_some
from src.model.entity.tacitEntity import TacitEntity
from src.model.entity.animity import most_specific
from src.model.syntax.syntacticAnalyzer import SyntacticAnalyzer


class ActiveVoiceSyntacticAnalyzer(SyntacticAnalyzer):
    def __init__(self, clause):
        SyntacticAnalyzer.__init__(self, clause)

    def subject(self):
        #print "Entering ActiveVoiceSyntacticAnalyzer.subject()"
        clause = self.clause
        if clause.is_gerund():
            subject = []
            return subject

        verbal_animity = clause.verb.subject_animity
        entities = self.verb_matching_subject_entities(4, 3)
        entities = self.filter_by_animity(entities, verbal_animity)
        if entities:
            entities[0].msi["animity"] = most_specific(verbal_animity, entities[0].msi["animity"])
            return [entities[0]]
        else:
            return self.tacit_or_implicit_subject(verbal_animity)

    def tacit_or_implicit_subject(self, verbal_animity="bianimate"):
        #print "Subject is tacit or implicit"

        if self.is_root_relative_clause():
            is_implicit = True
            entity = get_entity_some(verbal_animity, is_implicit)

        elif self.clause.has_kind_of_cataphoric_structure():
            entity = this()

        else:
            entity = self.tacit_subject(verbal_animity)

        return [entity]

    def is_root_relative_clause(self):
        clause = self.clause
        return clause.is_relative() and clause.is_root()

    def tacit_subject(self, verbal_animity="bianimate"):
        verb = self.clause.verb
        pronoun = verb.matching_pronoun()
        pronoun_msi = verb.matching_pronoun_msi()

        if pronoun_msi['person'] in [1,2]:
            pronoun_msi['animity'] = "animated"
        elif pronoun_msi['person'] is 3:
            pronoun_msi['animity'] = verbal_animity

        return TacitEntity(pronoun, pronoun_msi)

    def od(self):
        #print "Entering ActiveVoiceSyntacticAnalyzer.od()"
        verbal_animity = self.clause.verb.affected_object_animity

        nominal_entities_at_same_level_nodes = \
                self.find_entities_by(lambda: self.search_nominal_od_at_same_level_nodes("right", 3, verbal_animity),
                                      lambda: self.search_nominal_od_at_same_level_nodes("left", 2, verbal_animity))

        nominal_entities_under_prep_a = \
                self.find_entities_by(lambda: self.search_nominal_od_under_prep_a("right", 4, "animated"),
                                      lambda: self.search_nominal_od_under_prep_a("left", 3, "animated"))

        pronominal_entities = \
                self.find_entities_by(lambda: self.search_pronoun_at("right", 3, verbal_animity),
                                      lambda: self.search_pronoun_at("left", 3, verbal_animity))

        entities = nominal_entities_at_same_level_nodes
        entities += nominal_entities_under_prep_a if verbal_animity is not "inanimate" else []
        entities += pronominal_entities

        if not entities:
            is_implicit=True
            return [get_entity_some(verbal_animity, is_implicit)]

        entities[0].msi["animity"] = most_specific(entities[0].msi["animity"], verbal_animity)
        if not entities[0].is_subordinated_with_preposition("a"):
            return [entities[0]]

        # Has prep "a"
        entities[0].msi["animity"] = "animated"
        linked = self.link_duplicated_od_for(entities)
        if not linked:
            return [entities[0]]

        # Found linked
        linked.msi["animity"] = "animated"
        return [entities[0], linked]

    def link_duplicated_od_for(self, entities):
        acusative_pronoun = self.search_duplicated_od_for(entities)
        if acusative_pronoun:
            acusative_pronoun.add_coreference(entities[0])
            entities.append(acusative_pronoun)

        return acusative_pronoun

    def search_duplicated_od_for(self, entities):

        source_od = entities[0]

        closest_entities = self.clause.entities_closest_to_verb(("left", 3), ("right", 2))
        acusative_pronouns = self.only_acusative_pronouns_of(closest_entities)
        matching_pronouns = filter(lambda pronoun: source_od.matches(pronoun),
                                   acusative_pronouns)

        if len(matching_pronouns) > 1:
            raise Exception("Se encontró más de un pronombre duplicando el OD.")

        if not matching_pronouns:
            return None

        result = matching_pronouns[0] if matching_pronouns[0] != source_od else None

        return result

    def oi(self):
        #print "Entering ActiveVoiceSyntacticAnalyzer.oi()"
        entities = self.find_entities_by(lambda: self.search_nominal_oi_at("right", 3, "animated"),
                                         lambda: self.search_nominal_oi_at("left", 3, "animated"),
                                         lambda: self.search_pronoun_at("left", 2, "animated"),
                                         lambda: self.search_pronoun_at("right", 2, "animated"))
        if entities:
            entities[0].msi["animity"] = most_specific(entities[0].msi["animity"], "animated")
            return [entities[0]]
        else:
            return []

    def regimen(self):
        #print "Entering ActiveVoiceSyntacticAnalyzer.regimen()"
        verbal_animity = self.clause.verb.affected_object_animity
        at_right = lambda: self.search_regime_at("right", 3, verbal_animity)
        at_left  = lambda: self.search_regime_at("left", 2, verbal_animity)
        entities = self.find_entities_by(at_right, at_left)
        if entities:
            entities[0].msi["animity"] = most_specific(entities[0].msi["animity"], verbal_animity)
            return [entities[0]]
        else:
            return []

    def equative(self):
        #print "Entering ActiveVoiceSyntacticAnalyzer.equative()"
        verbal_animity = self.clause.verb.affected_object_animity
        entities = self.valid_subject_entities(2, 3) + self.search_subords_with_prep_at("right", 3, "de", "para")
        entities = self.filter_by_animity(entities, verbal_animity)
        if entities:
            entities[0].msi["animity"] = most_specific(entities[0].msi["animity"], verbal_animity)
            return [entities[0]]
        else:
            return []

    def search_regime_at(self, side, distance, verbal_animity):
        entities = self.search_subords_with_prep_at(side, distance, "a", "por", "en", "de", "contra", "con", "sobre")
        entities = self.filter_by_animity(entities, verbal_animity)

        if entities:
            return [entities[0]]
        else:
            return []

    def search_nominal_oi_at(self, side, distance, animity="bianimate"):
        entities = self.search_subords_with_prep_at(side, distance, "a", "para")
        entities = self.filter_infinitives(entities)
        entities = self.filter_by_animity(entities, animity)
        return entities

    def search_nominal_od_at_same_level_nodes(self, side, distance, verbal_animity="bianimate"):
        entities = self.clause.entities_closest_to_verb_at(side, distance)
        entities = self.only_nominal_of(entities)
        entities = self.filter_by_animity(entities, verbal_animity)
        return entities

    def search_nominal_od_under_prep_a(self, side, distance, verbal_animity="bianimate"):
        entities = self.search_subords_with_prep_at(side, distance, "a")
        entities = self.filter_infinitives(entities)
        entities = self.filter_by_animity(entities, verbal_animity)
        return entities
