#-*- coding: utf-8 -*-
from src.model.anaphora.personalPronounCoreferenceSearcher import PersonalPronounCoreferenceSearcher
from src.model.entity.linkedEntity import LinkedEntity


class PersonalPronounSolver:
    def __init__(self, clause, context):
        self.clause = clause
        self.context = context

    def solve(self):
        for pronoun, structure in self.pronouns_in_order():
            self.link(structure, pronoun)

    def link(self, structure, entity):
        referenced_entity = PersonalPronounCoreferenceSearcher(self.clause, self.context, entity).search()
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

        ordered = sorted(pronouns_with_structure, key = lambda (pronoun, structure): clause.index_of(pronoun, True) )
        return ordered

    def only_valid_pronouns(self, entities):
        is_valid_personal_pronoun = lambda entity: entity.category() == "pronoun" and entity.msi["type"] == "personal"\
            and entity.msi["person"] == 3 and entity.msi["case"] in [None, "acusative"]

        is_valid_indefinite_pronoun = lambda entity: entity.category() == "pronoun" \
            and entity.msi["type"] == "indefinite" and entity.lexical_form.lower() in [ "ambos", "ambas" ]

        is_valid_pronoun = lambda entity: is_valid_personal_pronoun(entity) or is_valid_indefinite_pronoun(entity)

        return filter(is_valid_pronoun, entities)