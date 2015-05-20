# -*- coding: utf-8 -*-
from src.model.entity.animityEnum import AnimityEnum

class SyntacticAnalyzer(object):
    def __init__(self, clause):
        self.clause = clause

    def analyze(self, clause):
        # print "Entering SyntacticAnalyzer.analyze(). Clause: ", clause

        # The order in which the FSynStr are extracted matters.
        for structure in clause.syntactic_structures:
            # assigned = filter(lambda p_ent: clause.is_assigned(p_ent), clause.all_entities())
            # unassigned = filter(lambda p_ent: not clause.is_assigned(p_ent), clause.all_entities())
            # print "--------------"
            # print "Assigned entities for clause: ", assigned, "\nUnassigned entities for clause: ", unassigned, "\n"

            if structure.is_empty():
                slot_name = structure.name
                method_get_slot_entities = getattr(self, slot_name, lambda: [])

                entities = method_get_slot_entities()

                structure.append_all(entities)

            # print "\nFINAL Entities for ", structure.name, ": ", structure.all_entities()
            # print "--------------"

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
        entities = sum(entities, [])
        instrument_goal = filter(lambda p_entity: p_entity.is_maximal_regarding(entities), entities)
        return instrument_goal

    def adjuncts(self):
        lonely = self.clause.lonely_entities()
        adjuncts = filter(lambda p_entity: p_entity.is_maximal_regarding(lonely), lonely)
        return adjuncts

    def search_instrument_goal_at(self, side, distance):
        return SyntacticAnalyzer.filter_infinitives(self.search_subords_with_prep_at(side, distance, ))

    def find_entities_by(self, *methods):
        # print "Entering find_entities_by"
        for method in methods:
            entities = method()
            if entities:
                return entities

        return []

    def verb_matching_subject_entities(self, distance_at_left, distance_at_right, left_to_right=True):
        # print "Entering SyntacticAnalyzer.verb_matching_subject_entities()"

        valid_subject_entities = self.valid_subject_entities(distance_at_left, distance_at_right, left_to_right)
        verb_matching_entities = filter(lambda entity: self.clause.verb.matches(entity),
                                        valid_subject_entities)
        return verb_matching_entities

    def valid_subject_entities(self, distance_at_left, distance_at_right, left_to_right=True):
        # print "Entering SyntacticAnalyzer.valid_subject_entities()"
        clause = self.clause

        entities_l = clause.entities_closest_to_verb_at("left", distance_at_left)
        entities_r = clause.entities_closest_to_verb_at("right", distance_at_right)

        if left_to_right:
            entities = entities_l + entities_r
        else:
            entities = entities_r + entities_l

        valid_subject_entities = self.only_valid_subject_entities_of(entities)
        return valid_subject_entities

    @staticmethod
    def filter_group_sp_inf(entities):
        entities_without_group_sp_inf = filter(lambda entity: entity.node.label is not "group-sp-inf",
                                               entities)
        return entities_without_group_sp_inf

    @staticmethod
    def filter_infinitives(entities):
        entities_without_infs = filter(lambda entity: not entity.has_attr("infinitive"),
                                       entities)
        return entities_without_infs

    @staticmethod
    def filter_by_animity(entities, verbal_animity):
        filtered_entities = filter(lambda entity: entity.animity_matches(verbal_animity),
                                   entities)
        return filtered_entities

    def search_subord_with_prep_at(self, side, distance, *accepted_prepositions):

        def which(node):
            return self.starts_with_accepted_preposition(node, *accepted_prepositions)

        entities = self.search_subord_at(side, distance, which)
        return entities

    def search_subords_with_prep_at(self, side, distance, *accepted_prepositions):
        # print "Entering SyntacticAnalyzer.search_subords_with_prep_at()"

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
        # print "Entering SyntacticAnalyzer.search_subords_at() - side ", str(side), " - distance ", str(distance)
        all_subord_entities = self.clause.subord_entities_closest_to_verb_at(side, distance, which)
        all_subord_entities = [sorted(entities, key=lambda entity: entity.level())
                               for entities in all_subord_entities]

        subord_entities = [item for sublist in all_subord_entities for item in sublist]

        return subord_entities

    def search_pronoun_at(self, side, distance, animity=AnimityEnum.bianimate):
        pronouns = self.only_pronouns_of(self.clause.entities_closest_to_verb_at(side, distance))
        pronouns = SyntacticAnalyzer.filter_by_animity(pronouns, animity)

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
        return filter(lambda entity: entity.category() == "pronoun" and entity.msi["case"] == "accusative",
                      entities)

    def only_valid_subject_entities_of(self, entities):
        is_valid_pronoun = lambda entity: entity.category() == "pronoun" \
                                          and entity.msi["case"] in [None, "personal", "demonstrative", "nominative"]
        valid_subject_entities = \
            filter(lambda entity: not entity.node.label == "patons"
                                  and (entity.category() in ["noun", "determinant"] or is_valid_pronoun(entity)),
                   entities)
        return valid_subject_entities

    def only_nominal_of(self, entities):
        nominal_entities = filter(lambda entity: entity.category() == "noun", entities)
        return nominal_entities

    instrument_goal_preps = ["sin", "con", "contra", "en_favor_de", "a_favor_de", "en_defensa_de",
                             "en_contra_de", "en_pos_de", "mediante", "a_través_de", "por_medio_de",
                             "gracias_a", "merced_a"]