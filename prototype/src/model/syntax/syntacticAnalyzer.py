#-*- coding: utf-8 -*-
from src.model.syntax.syntacticStructure import SyntacticStructure

class SyntacticAnalyzer:
    def __init__(self, clause):
        self.clause = clause

    def analyze(self, structures_to_analyze):
        # El orden en que se extraen las FSS es importante.
        for name in structures_to_analyze:
            structure = getattr(self, name, lambda: SyntacticStructure(name))()
            self.clause.syntactic_structures.append(structure)

    def subject(self):
        structure = SyntacticStructure("subject")
        entities = self.clause.lonely_entities()
        structure.entities = [ entities[0] ] if entities else []
        return structure

    def verb(self):
        verb = SyntacticStructure("verb")
        verb.entities.append(self.clause.verb)
        return verb

    def adjuncts(self):
        structure = SyntacticStructure("adjuncts")
        structure.entities = self.clause.lonely_entities()
        return structure

    def extract_searching(self, name, *methods):
        structure = SyntacticStructure(name)
        structure.entities = self.find_entities_by(methods)
        return structure

    def find_entities_by(self, methods):
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

    def search_subord_with_preposition_at(self, side, distance, *accepted_prepositions):
        def which(node):
            first_leaf = node.leaves()[0]
            return first_leaf.msi["type"] == "preposition" and \
                first_leaf.lexical_form.lower() in accepted_prepositions if accepted_prepositions else True
        return self.search_subord_at(side, distance, which)

    def search_subord_at(self, side, distance, which = lambda node: True):
        all_subord_entities = self.clause.subord_entities_closest_to_verb_at(side, distance, which)
        return all_subord_entities[0] if all_subord_entities else []

    def search_pronoun_at(self, side, distance):
        return self.only_pronouns_of(self.clause.entities_closest_to_verb_at(side, distance))

    def only_pronouns_of(self, entities):
        return filter(lambda entity: entity.category() == "pronoun", entities)

    def only_acusative_pronouns_of(self, entities):
        return filter(lambda entity: entity.category() == "pronoun" and entity.msi["case"] == "acusative", entities)

    def only_valid_subject_entities_of(self, entities):
        is_valid_pronoun = lambda entity: entity.category() == "pronoun" and entity.msi["case"] \
            in [None, "personal", "demostrative"]
        return filter(lambda entity: entity.category() == "noun" or entity.category() == "determinant" or
                      is_valid_pronoun(entity), entities)

    def only_nominal_of(self, entities):
        return filter(lambda entity: entity.category() == "noun", entities)