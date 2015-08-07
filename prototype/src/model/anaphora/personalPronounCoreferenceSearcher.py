# -*- coding: utf-8 -*-
from itertools import chain
from src.utils.tree.treeNode import TreeNode

debug_mode = True


class PersonalPronounCoreferenceSearcher:

    def __init__(self, clause, context, pronoun):
        self.clause = clause
        self.context = context

        self.pronoun = pronoun
        self.pronoun_index = self.compute_pronoun_index()

    def search(self):
        if debug_mode: print "--> PersonalPronounCoreferenceSearcher.search() - pronoun: ", self.pronoun
        methods = [self.search_in_parent_clauses,
                   self.search_in_previous_clauses,
                   self.search_in_previous_sentences]

        entity = self.first_non_none((method() for method in methods))
        if debug_mode: print "<-- search()  --> entity: ", entity
        return entity

    def search_in_parent_clauses(self):
        if not self.clause.is_root():
            return self.first_non_none((self.search_in(parent) for parent in self.clause.path_to_root()))

    def search_in_previous_clauses(self):
        current_clause_root = self.clause.root()
        previous_main_clauses = filter(lambda clause: clause.is_root() and clause != current_clause_root,
                                       self.context["clauses"][::-1])

        search_in_main_clause = lambda clause: self.search_in_clauses(self.sorted(list(clause)))
        return self.first_non_none((search_in_main_clause(clause) for clause in previous_main_clauses))

    def search_in_previous_sentences(self):
        previous_sentences = self.context["sentences"]
        if not previous_sentences:
            return None
        selected_sentences = previous_sentences[::-1][0:1]
        clauses = sum([self.sorted(sentence.clauses) for sentence in selected_sentences], [])
        return self.search_in_clauses(clauses)

    def search_in_clauses(self, clauses):
        return self.first_non_none((self.search_in(clause) for clause in clauses))

    def search_in(self, clause):
        if not self.is_already_read(clause):
            return

        for structure_name in self.search_order_for(clause):
            if not clause.has_structure(structure_name):
                continue

            structure = clause.structure(structure_name)
            entities = self.entities_to_be_searched_in(structure)
            entities = self.only_matching_entities(entities, clause)
            entities = filter(lambda entity: entity.matches_animity_of(self.pronoun),
                              entities)

            already_placed_entities = self.clause.assigned_entities_with_referenced_ones()
            non_linked_entities = filter(lambda entity: entity not in already_placed_entities,
                                         entities)
            if non_linked_entities:
                return non_linked_entities[0]

    def is_already_read(self, clause):
        return self.clause.root() != clause.root() or clause in self.context["clauses"]

    def entities_to_be_searched_in(self, structure):
        entities = []
        non_trace_entities = filter(lambda p_entity: not p_entity.is_trace(), structure.all_entities())
        for entity in non_trace_entities:
            if not entity.has_attr("infinitive"):
                entities.append(entity)

            if entity.is_coordinated() or entity.has_attr("infinitive"):
                entities.extend(entity.children)

        return entities

    def only_matching_entities(self, entities, entities_clause):
        matching_entities = filter(lambda entity: entity.matches(self.pronoun),
                                   entities)
        if entities_clause.root() == self.clause.root():
            matching_entities = self.only_already_read_entities(matching_entities, entities_clause)
        return matching_entities

    def only_already_read_entities(self, entities, entities_clause):
        clause = entities_clause
        return filter(lambda entity: entity.is_linked() or entity.is_tacit() or \
                      (clause.index_in_root_of(entity.node) < self.pronoun_index), entities)

    def sorted(self, clauses):
        clauses_by_level = TreeNode.by_level(clauses)
        clauses_lists = zip(*sorted(clauses_by_level.items()))[1]
        clauses_lists = [ list_for_level[::-1] for list_for_level in clauses_lists ] # En orden reverso de lectura
        return list(chain(*clauses_lists))

    def first_non_none(self, generator):
        return next((x for x in generator if x is not None), None)

    def compute_pronoun_index(self):
        node_for_index = self.pronoun.node if not self.pronoun.is_tacit() else self.clause.proper_tree().leaves()[0]
        return self.clause.index_in_root_of(node_for_index)

    def search_order_for(self, clause):
        pronoun_case = self.pronoun.msi["case"]
        return PersonalPronounCoreferenceSearcher.search_order_by_voice[clause.voice][pronoun_case]

    search_order_by_voice = {"active":  {None:         ["subject", "od", "oi", "regimen", "equative",
                                                        "instrument_goal", "adjuncts"],
                                         "accusative": ["od", "subject", "regimen", "oi", "equative",
                                                        "instrument_goal", "adjuncts"]
                                         },
                             "passive": {None:         ["od", "subject", "instrument_goal", "adjuncts"],
                                         "accusative": ["subject", "od", "instrument_goal", "adjuncts"]
                                         },
                             None:      {None:         ["subject", "instrument_goal"],
                                         "accusative": ["subject", "instrument_goal"]
                                         }
                             }
