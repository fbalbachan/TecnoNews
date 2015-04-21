# -*- coding: utf-8 -*-
from src.model.entity.entity import Entity
from src.model.entity.animity_enum import AnimityEnum


class SyntacticAnalyzer:
    def __init__(self, clause):
        self.clause = clause

    def analyze(self, clause):
        # The order in which the FSS are extracted matters.
        for structure in clause.syntactic_structures:
            if structure.is_empty():
                # print "\n\nEntities for ", structure.name, " before calculus", structure.all_entities(), "\n\n"

                get_slot_entities_method = getattr(self, structure.name, lambda: [])
                entities = get_slot_entities_method()
                structure.append_all(entities)

                # print "\n\nEntities for ", structure.name, " after calculus", structure.all_entities(), "\n\n"

    def subject(self):
        # print "Entering SyntacticAnalyzer.subject()"
        entities = self.clause.lonely_entities()
        return [entities[0]] if entities else []

    def verb(self):
        # print "Entering SyntacticAnalyzer.verb()"
        return [self.clause.verb]

    def instrument_goal(self):
        def which(node):
            return self.starts_with_accepted_preposition(node, *self.instrument_goal_preps)
        entities = self.clause.subord_entities(which)
        return Entity.only_maximal(sum(entities, []))

    def adjuncts(self):
        return Entity.only_maximal(self.clause.lonely_entities())

    def search_instrument_goal_at(self, side, distance):
        return self.filter_infinitives(self.search_subords_with_prep_at(side, distance, ))

    def find_entities_by(self, *methods):
        for method in methods:
            entities = method()
            if entities:
                return entities

        return []

    def verb_matching_subject_entities(self, distance_at_left, distance_at_right):
        valid_subject_entities = self.valid_subject_entities(distance_at_left, distance_at_right)
        verb_matching_entities = filter(lambda entity: self.clause.verb.matches(entity),
                                        valid_subject_entities)
        return verb_matching_entities

    def valid_subject_entities(self, distance_at_left, distance_at_right):
        clause = self.clause
        entities = clause.entities_closest_to_verb_at("left", distance_at_left) \
                 + clause.entities_closest_to_verb_at("right", distance_at_right)
        valid_subject_entities = self.only_valid_subject_entities_of(entities)
        return valid_subject_entities

    def filter_group_sp_inf(self, entities):
        entities_without_group_sp_inf = filter(lambda entity: entity.node.label is not "group-sp-inf",
                                               entities)
        return entities_without_group_sp_inf

    def filter_infinitives(self, entities):
        entities_without_infs = filter(lambda entity: not entity.has_attr("infinitive"),
                                       entities)
        return entities_without_infs

    def filter_by_animity(self, entities, verbal_animity):
        filtered_entities = filter(lambda entity: entity.animity_matches(verbal_animity),
                                   entities)
        return filtered_entities

    def search_subord_with_prep_at(self, side, distance, *accepted_prepositions):

        def which(node):
            return self.starts_with_accepted_preposition(node, *accepted_prepositions)

        entities = self.search_subord_at(side, distance, which)
        return entities

    def search_subords_with_prep_at(self, side, distance, *accepted_prepositions):

        def which(node):
            return self.starts_with_accepted_preposition(node, *accepted_prepositions)

        entities = self.search_subords_at(side, distance, which)
        return entities

    def search_first_subord_with_prep_at(self, side, distance, *accepted_prepositions):
        entities = self.search_subords_with_prep_at(side, distance, *accepted_prepositions)

        if entities:
            return [entities[0]]
        else:
            return []

    def starts_with_accepted_preposition(self, node, *accepted_prepositions):
        first_leaf = node.leaves()[0]
        return first_leaf.msi["type"] == "preposition" \
               and first_leaf.lexical_form in accepted_prepositions if accepted_prepositions else True

    def search_subord_at(self, side, distance, which=lambda node: True):
        all_subord_entities = self.clause.subord_entities_closest_to_verb_at(side, distance, which)
        all_subord_entities = [sorted(entities, key=lambda entity: entity.level())
                               for entities in all_subord_entities]
        return all_subord_entities[0] if all_subord_entities else []

    def search_subords_at(self, side, distance, which=lambda node: True):
        all_subord_entities = self.clause.subord_entities_closest_to_verb_at(side, distance, which)
        all_subord_entities = [sorted(entities, key=lambda entity: entity.level())
                               for entities in all_subord_entities]

        subord_entities = [item for sublist in all_subord_entities for item in sublist]
        return subord_entities

    def search_pronoun_at(self, side, distance, animity=AnimityEnum.bianimate):
        pronouns = self.only_pronouns_of(self.clause.entities_closest_to_verb_at(side, distance))
        pronouns = self.filter_by_animity(pronouns, animity)

        if pronouns:
            return [pronouns[0]]
        else:
            return []

    def search_pronouns_at(self, side, distance):
        pronouns = self.only_pronouns_of(self.clause.entities_closest_to_verb_at(side, distance))
        return pronouns

    def only_pronouns_of(self, entities):
        return filter(lambda entity: entity.category() == "pronoun",
                      entities)

    def only_accusative_pronouns_of(self, entities):
        return filter(lambda entity: entity.category() == "pronoun"
                                     and entity.msi["case"] == "acusative",
                      entities)

    def only_valid_subject_entities_of(self, entities):
        is_valid_pronoun = lambda entity: entity.category() == "pronoun" \
                                          and entity.msi["case"] in [None, "personal", "demonstrative", "nominative"]

        valid_subject_entities = filter(lambda entity: not entity.node.label == "patons"
                                                       and (entity.category() in ["noun", "determinant"]
                                                            or is_valid_pronoun(entity)),
                                        entities)
        return valid_subject_entities

    def only_nominal_of(self, entities):
        nominals = filter(lambda entity: entity.category() == "noun", entities)
        return nominals

    instrument_goal_preps = ["sin", "con", "contra", "en_favor_de", "a_favor_de", "en_defensa_de",
                             "en_contra_de", "en_pos_de", "mediante", "a_través_de", "por_medio_de",
                             "gracias_a", "merced_a"]