#-*- coding: utf-8 -*-
from itertools import chain
from src.utils.treeNode import TreeNode

class PersonalPronounCoreferenceSearcher:
    def __init__(self, clause, context, pronoun):
        self.clause = clause
        self.context = context
        self.pronoun = pronoun

    def search(self):
        methods = [ self.search_in_parent_clauses, self.search_in_previous_clauses, self.search_in_previous_sentences ]
        return self.first_non_none(( method() for method in methods ))

    def search_in_parent_clauses(self):
        if not self.clause.is_root():
            return self.first_non_none( ( self.search_in(parent) for parent in self.clause.path_to_root() ) )

    def search_in_previous_clauses(self):
        current_clause_root = self.clause.root()
        previous_main_clauses = filter(lambda clause: clause.is_root() and clause != current_clause_root,
                                       self.context["clauses"][::-1])

        search_in_main_clause = lambda clause: self.search_in_clauses(self.sorted(list(clause)))
        return self.first_non_none( ( search_in_main_clause(clause) for clause in previous_main_clauses ) )

    def search_in_previous_sentences(self):
        previous_sentences = self.context["sentences"]
        if not previous_sentences: return None
        selected_sentences = previous_sentences[::-1][0:1]
        clauses = sum([ self.sorted(sentence.clauses) for sentence in selected_sentences], [])
        return self.search_in_clauses(clauses)

    def search_in_clauses(self, clauses):
        return self.first_non_none( ( self.search_in(clause) for clause in clauses ) )

    def search_in(self, clause):
        pronoun = self.pronoun
        for structure_name in self.search_order_for(clause):
            if not clause.has_structure(structure_name): continue
            structure = clause.structure(structure_name)

            entities = []
            for entity in structure.entities:
                entities.append(entity)
                if not entity.is_tacit() and entity.is_coordinated(): entities.extend(entity.children)

            matching_entities = filter(lambda entity: entity.matches(pronoun), entities)

            already_placed_entities = self.clause.assigned_entities_with_referenced_ones()
            non_linked_entities = filter(lambda entity: entity not in already_placed_entities, matching_entities)

            if non_linked_entities: return non_linked_entities[0]

    def sorted(self, clauses):
        clauses_by_level = TreeNode.by_level(clauses)
        clauses_lists = zip(*sorted(clauses_by_level.items()))[1]
        clauses_lists = [ list_for_level[::-1] for list_for_level in clauses_lists ] # En orden reverso de lectura
        return list(chain(*clauses_lists))

    def first_non_none(self, generator):
        return next( (x for x in generator if x is not None), None)

    def search_order_for(self, clause):
        pronoun_case = self.pronoun.msi["case"]
        return PersonalPronounCoreferenceSearcher.search_order_by_voice[clause.voice][pronoun_case]

    search_order_by_voice = { "active" : { None         : [ "subject", "od", "oi", "regimen", "equative", "adjuncts" ],
                                          "acusative"   : ["od", "subject", "regimen", "oi", "equative", "adjuncts" ]},
                             "passive" : { None         : [ "od", "subject", "adjuncts" ],
                                          "acusative"   : ["subject", "od", "adjuncts"] },
                             None      : { None         : [ "subject" ] } }