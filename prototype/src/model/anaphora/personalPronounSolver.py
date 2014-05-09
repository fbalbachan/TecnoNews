#-*- coding: utf-8 -*-
from src.model.entity.linkedEntity import LinkedEntity

class PersonalPronounSolver:
    def __init__(self, clause, context):
        self.clause = clause
        self.context = context

    def solve(self):
        for pronoun, structure in self.pronouns_in_order():
            self.link(structure, pronoun)

    def link(self, structure, entity):
        referenced_entity = self.search_referenced_entity_for(entity)
        if referenced_entity:
            linked_entity = LinkedEntity(entity, referenced_entity)
            structure.replace(entity, linked_entity)
            self.clause.linked_entities.append(linked_entity)

    def pronouns_in_order(self):
        clause = self.clause
        is_valid_pronoun = lambda entity: entity.category() == "pronoun" and entity.msi["type"] == "personal" \
            and entity.msi["person"] == 3 and entity.msi["case"] in [None, "acusative"]

        pronouns_with_structure = []
        for structure in clause.syntactic_structures:
            pronouns = filter(is_valid_pronoun, structure.all_entities())
            for pronoun in pronouns:
                pronouns_with_structure.append( (pronoun, structure) )

        ordered = sorted(pronouns_with_structure, key = lambda (pronoun, structure): float("-inf") if pronoun.is_tacit()
                         else clause.proper_leaves().index(pronoun.leaves()[0]) )
        return ordered

    def search_referenced_entity_for(self, actual_entity):
        if not self.clause.is_relative():
            entity = self.search_referenced_entity_in_clauses(self.context["clauses"][::-1], actual_entity)
            if entity: return entity
        return self.search_referenced_entity_in_sentences_for(actual_entity)

    def search_referenced_entity_in_sentences_for(self, actual_entity):
        previous_sentences = self.context["sentences"]
        if not previous_sentences: return None
        selected_sentences = previous_sentences[::-1][0:3]
        clauses = [sentence.main_clause() for sentence in selected_sentences]
        return self.search_referenced_entity_in_clauses(clauses, actual_entity)

    def search_referenced_entity_in_clauses(self, clauses, actual_entity):
        for clause in clauses:
            entity = self.search_referenced_entity_in(clause, actual_entity)
            if entity: return entity
        return None

    def search_referenced_entity_in(self, clause, actual_entity):
        for structure_name in self.search_order_for(clause, actual_entity):
            if not clause.has_structure(structure_name): continue
            structure = clause.structure(structure_name)

            matching_entities = filter(lambda entity: entity.matches(actual_entity), structure.entities)

            linked_entities = [ entity.referenced_entity for entity in self.clause.linked_entities ]
            non_linked_entities = filter(lambda entity: entity not in linked_entities, matching_entities)

            if non_linked_entities: return non_linked_entities[0]
        return None

    def search_order_for(self, clause, pronoun):
        pronoun_case = pronoun.msi["case"]
        return PersonalPronounSolver.search_order_by_voice[clause.voice][pronoun_case]

    search_order_by_voice = { "active" : { None: [ "subject", "od", "oi", "regimen", "equative", "adjuncts" ],
                                          "acusative": ["od", "subject", "regimen", "oi", "equative", "adjuncts" ]},
                             "passive" : { None: [ "od", "subject", "adjuncts" ],
                                          "acusative": ["subject", "od", "adjuncts"] },
                             None : { None: [ "subject" ] } }