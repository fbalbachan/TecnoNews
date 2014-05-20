#-*- coding: utf-8 -*-

from itertools import chain

from src.model.entity.linkedEntity import LinkedEntity
from src.utils.treeNode import TreeNode


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
        pronouns_with_structure = []
        for structure in clause.syntactic_structures:
            pronouns = self.only_valid_pronouns(structure.all_entities())
            for pronoun in pronouns:
                pronouns_with_structure.append( (pronoun, structure) )

        ordered = sorted(pronouns_with_structure, key = lambda (pronoun, structure): float("-inf") if pronoun.is_tacit()
                         else clause.proper_leaves().index(pronoun.leaves()[0]) )
        return ordered

    def only_valid_pronouns(self, entities):
        is_valid_personal_pronoun = lambda entity: entity.category() == "pronoun" and entity.msi["type"] == "personal"\
            and entity.msi["person"] == 3 and entity.msi["case"] in [None, "acusative"]

        is_valid_indefinite_pronoun = lambda entity: entity.category() == "pronoun" \
            and entity.msi["type"] == "indefinite" and entity.lexical_form.lower() in [ "ambos", "ambas" ]

        is_valid_pronoun = lambda entity: is_valid_personal_pronoun(entity) or is_valid_indefinite_pronoun(entity)

        return filter(is_valid_pronoun, entities)

    def search_referenced_entity_for(self, actual_entity):
        if not self.clause.is_root():
            for parent in self.clause.path_to_root():
                entity = self.search_referenced_entity_in(parent, actual_entity)
                if entity: return entity

        entity = self.search_referenced_entity_in_previous_clauses_for(actual_entity)
        if entity: return entity

        return self.search_referenced_entity_in_sentences_for(actual_entity)

    def search_referenced_entity_in_previous_clauses_for(self, actual_entity):
        actual_root = self.clause.root()
        previous_root_clauses = filter(lambda clause: clause.is_root() and clause != actual_root,
                                       self.context["clauses"][::-1])
        for root_clause in previous_root_clauses:
            sorted_by_level = self.sorted_by_level_in_reverse_order(list(root_clause))
            entity = self.search_referenced_entity_in_clauses(sorted_by_level, actual_entity)
            if entity: return entity
        return None

    def search_referenced_entity_in_sentences_for(self, actual_entity):
        previous_sentences = self.context["sentences"]
        if not previous_sentences: return None
        selected_sentences = previous_sentences[::-1][0:1]
        clauses = []
        for sentence in selected_sentences:
            clauses.extend(self.sorted_by_level_in_reverse_order(sentence.clauses))
        return self.search_referenced_entity_in_clauses(clauses, actual_entity)

    def sorted_by_level_in_reverse_order(self, clauses):
        clauses_by_level = TreeNode.by_level(clauses)
        clauses_lists = zip(*sorted(clauses_by_level.items()))[1]
        clauses_lists = [ list_for_level[::-1] for list_for_level in clauses_lists ] # En orden reverso de lectura
        return list(chain(*clauses_lists))

    def search_referenced_entity_in_clauses(self, clauses, actual_entity):
        for clause in clauses:
            entity = self.search_referenced_entity_in(clause, actual_entity)
            if entity: return entity
        return None

    def search_referenced_entity_in(self, clause, actual_entity):
        for structure_name in self.search_order_for(clause, actual_entity):
            if not clause.has_structure(structure_name): continue
            structure = clause.structure(structure_name)

            entities = []
            for entity in structure.entities:
                entities.append(entity)
                if not entity.is_tacit() and entity.is_coordinated(): entities.extend(entity.children)

            matching_entities = filter(lambda entity: entity.matches(actual_entity), entities)

            already_placed_entities = self.clause.assigned_entities_with_referenced_ones()
            non_linked_entities = filter(lambda entity: entity not in already_placed_entities, matching_entities)

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