#-*- coding: utf-8 -*-
from src.model.syntacticStructure import SyntacticStructure

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

    def nominal_and_personal_entities(self, distance_at_left, distance_at_right):
        clause = self.clause
        entities = clause.entities_closest_to_verb_at("left", distance_at_left) \
                    + clause.entities_closest_to_verb_at("right", distance_at_right)

        only_nominal_and_personal_pronouns = self.only_nominal(entities) + self.only_personal_pronouns_of(entities)
        verb_matching_entities = filter(lambda entity: clause.verb.matches(entity), only_nominal_and_personal_pronouns)
        return verb_matching_entities

    def search_subord_at(self, side, distance, which = lambda node: True):
        all_subord_entities = self.clause.subord_entities_closest_to_verb_at(side, distance, which)
        return all_subord_entities[0] if all_subord_entities else []

    def search_pronoun_at(self, side, distance):
        return self.only_pronouns_of(self.clause.entities_closest_to_verb_at(side, distance))

    def only_pronouns_of(self, entities):
        return filter(lambda entity: entity.category() == "pronoun", entities)

    def only_personal_pronouns_of(self, entities):
        return filter(lambda entity: entity.category() == "pronoun" and entity.msi["case"] == None, entities)

    def only_nominal(self, entities):
        return filter(lambda entity: entity.category() == "noun", entities)