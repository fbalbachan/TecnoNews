# -*- coding: utf-8 -*-

from ling.tacit_subjects import tacit_subject_for
from subject import *
from syntacticStructure import *


class ActiveVoiceSyntacticAnalyzer():
    def __init__(self, clause):
        self.clause = clause

    def analyze(self, structures_to_analyze):
        # El orden en que se extraen las FSS es importante.
        for name in structures_to_analyze:
            structure = getattr(self, name, lambda: SyntacticStructure(name))()
            self.clause.syntactic_structures.append(structure)

    def verb(self):
        verb = SyntacticStructure("verb")
        verb.entities.append(self.clause.verb)
        return verb

    def subject(self):
        clause = self.clause
        entities = clause.entities_closest_to_verb_at("left", 3) + clause.entities_closest_to_verb_at("right", 2)
        only_nominal_and_personal_pronouns = self.only_nominal(entities) + self.only_personal_pronouns_of(entities)

        verb_matching_entities = filter(lambda entity: clause.verb.matches(entity), only_nominal_and_personal_pronouns)
        if verb_matching_entities: return Subject.concrete(verb_matching_entities[0])

        verb = clause.verb
        tacit_msi = { "person" : verb.msi["person"], "number" : verb.msi["number"], "gender" : verb.msi["gender"] }
        return Subject.tacit(tacit_subject_for(verb), tacit_msi)

    def od(self):
        structure = SyntacticStructure("od")

        nominal_at_right = lambda: self.search_nominal_od_at("right", 3)
        nominal_at_left  = lambda: self.search_nominal_od_at("left", 2)
        pronominal_at_left  = lambda: self.search_pronoun_at("left", 1)

        search_methods = [ nominal_at_right, nominal_at_left, pronominal_at_left ]
        structure.entities = self.find_entities_by(search_methods)
        return structure

    def oi(self):
        structure = SyntacticStructure("oi")

        nominal_at_right = lambda: self.search_nominal_oi_at("right", 3)
        nominal_at_left  = lambda: self.search_nominal_oi_at("left", 3)
        pronominal_at_left  = lambda: self.search_pronoun_at("left", 1)

        search_methods = [ nominal_at_right, nominal_at_left, pronominal_at_left ]
        structure.entities = self.find_entities_by(search_methods)
        return structure

    def regimen(self):
        structure = SyntacticStructure("regimen")

        at_right = lambda: self.search_regime_at("right", 3)
        at_left  = lambda: self.search_regime_at("left", 2)

        search_methods = [ at_right, at_left ]
        structure.entities = self.find_entities_by(search_methods)
        return structure

    def adjuncts(self):
        structure = SyntacticStructure("regimen")
        structure.entities = self.clause.lonely_entities()
        return structure

    def find_entities_by(self, methods):
        for method in methods:
            entities = method()
            if entities: return entities
        return []

    # Duplicado con "search_nominal_od", oi, etc. Refactorizar.
    def search_regime_at(self, side, distance):
        clause = self.clause
        def which(node):
            first_leaf = node.leaves()[0]
            return first_leaf.msi["type"] == "preposition" and first_leaf.lexical_form.lower() in ["a", "con", "de"]

        all_subord_entities = clause.verb_level_subord_entities_at(side, distance, which)
        return all_subord_entities[0] if all_subord_entities else []

    def search_nominal_oi_at(self, side, distance):
        clause = self.clause
        def which(node):
            first_leaf = node.leaves()[0]
            return first_leaf.msi["type"] == "preposition" and first_leaf.lexical_form.lower() == "a"

        all_subord_entities = clause.verb_level_subord_entities_at(side, distance, which)
        return all_subord_entities[0] if all_subord_entities else []

    def search_pronoun_at(self, side, distance):
        return self.only_pronouns_of(self.clause.entities_closest_to_verb_at(side, distance))

    def search_nominal_od_at(self, side, distance):
        clause = self.clause
        entities = self.only_nominal(clause.entities_closest_to_verb_at(side, distance))
        if entities:
            return [ entities[0] ]
        else:
            all_subord_entities = clause.verb_level_subord_entities_at(side, distance)
            if all_subord_entities: return all_subord_entities[0]
        return []

    def only_pronouns_of(self, entities):
        return filter(lambda entity: entity.category() == "pronoun", entities)

    def only_personal_pronouns_of(self, entities):
        return filter(lambda entity: entity.category() == "pronoun" and entity.msi["case"] == None, entities)

    def only_nominal(self, entities):
        return filter(lambda entity: entity.category() == "noun", entities)

    def subordinated_verb_level_entities(self):
        pass
