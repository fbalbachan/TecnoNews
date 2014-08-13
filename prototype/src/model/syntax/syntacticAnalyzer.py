#-*- coding: utf-8 -*-
from src.model.entity.entity import Entity
from src.model.syntax.syntacticStructure import SyntacticStructure


class SyntacticAnalyzer:
    def __init__(self, clause):
        self.clause = clause

    def analyze(self, clause):
        # El orden en que se extraen las FSS es importante.
        for structure in clause.syntactic_structures:
            if structure.is_empty():
                entities = getattr(self, structure.name, lambda: [])()
                structure.append_all(entities)

    def subject(self):
        entities = self.clause.lonely_entities()
        return [ entities[0] ] if entities else []

    def verb(self):
        return [ self.clause.verb ]

    def instrument_goal(self):
        def which(node):
            return self.starts_with_accepted_preposition(node, *self.instrument_goal_preps)
        entities = self.clause.subord_entities(which)
        return Entity.only_maximal(sum(entities, []))

    def adjuncts(self):
        return Entity.only_maximal(self.clause.lonely_entities())

    def search_instrument_goal_at(self, side, distance):
        return self.without_infs(self.search_subord_with_prep_at(side, distance, ))

    def find_entities_by(self, *methods):
        for method in methods:
            entities = method()
            if entities: return entities
        return []

    def verb_matching_subject_entities(self, distance_at_left, distance_at_right):
        valid_subject_entities = self.valid_subject_entities(distance_at_left, distance_at_right)
        verb_matching_entities = filter(lambda entity: self.clause.verb.matches(entity), valid_subject_entities)
        return verb_matching_entities

    def valid_subject_entities(self, distance_at_left, distance_at_right):
        clause = self.clause
        entities = clause.entities_closest_to_verb_at("left", distance_at_left) \
                    + clause.entities_closest_to_verb_at("right", distance_at_right)
        valid_subject_entities = self.only_valid_subject_entities_of(entities)
        return valid_subject_entities

    def without_infs(self, entities):
        return filter(lambda entity: not entity.has_attr("infinitive"), entities)

    def search_subord_with_prep_at(self, side, distance, *accepted_prepositions):
        def which(node):
            return self.starts_with_accepted_preposition(node, *accepted_prepositions)
        entities = self.search_subord_at(side, distance, which)
        return entities

    def starts_with_accepted_preposition(self, node, *accepted_prepositions):
        first_leaf = node.leaves()[0]
        return first_leaf.msi["type"] == "preposition" and \
            first_leaf.lexical_form in accepted_prepositions if accepted_prepositions else True

    def search_first_subord_with_prep_at(self, side, distance, *accepted_prepositions):
        entities = self.search_subord_with_prep_at(side, distance, *accepted_prepositions)
        if entities: return [ entities[0] ]
        return entities

    def search_subord_at(self, side, distance, which = lambda node: True):
        all_subord_entities = self.clause.subord_entities_closest_to_verb_at(side, distance, which)
        all_subord_entities = [ sorted(entities, key = lambda entity: entity.level())
                               for entities in all_subord_entities ]
        return all_subord_entities[0] if all_subord_entities else []

    def search_pronoun_at(self, side, distance):
        pronouns = self.only_pronouns_of(self.clause.entities_closest_to_verb_at(side, distance))
        if pronouns: pronouns = [ pronouns[0] ]
        return pronouns

    def only_pronouns_of(self, entities):
        return filter(lambda entity: entity.category() == "pronoun", entities)

    def only_acusative_pronouns_of(self, entities):
        return filter(lambda entity: entity.category() == "pronoun" and entity.msi["case"] == "acusative", entities)

    def only_valid_subject_entities_of(self, entities):
        is_valid_pronoun = lambda entity: entity.category() == "pronoun" and entity.msi["case"] \
            in [None, "personal", "demostrative", "nominative"]
        return filter(lambda entity: entity.category() == "noun" or entity.category() == "determinant" or
                      is_valid_pronoun(entity), entities)

    def only_nominal_of(self, entities):
        return filter(lambda entity: entity.category() == "noun", entities)

    instrument_goal_preps = ["sin", "con", "contra", "en_favor_de", "a_favor_de", "en_contra_de", "en_pos_de",
                             "mediante", "a_través_de", "por_medio_de", "gracias_a"]
