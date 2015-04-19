# -*- coding: utf-8 -*-
from src.model.anaphora.personalPronounCoreferenceSearcher import PersonalPronounCoreferenceSearcher
from src.model.entity.verb import Verb
from src.model.entity.animity import Animity

class PersonalPronounSolver:
    def __init__(self, clause, context):
        self.clause = clause
        self.context = context

    def solve(self):
        for pronoun, structure in self.pronouns_in_order():
            self.link(structure, pronoun)

    def link(self, structure, pronoun):
        coref_searcher = PersonalPronounCoreferenceSearcher(self.clause, self.context, pronoun)
        referenced_entity = coref_searcher.search()
        if referenced_entity:
            if structure.name in Verb.boxes_with_scripted_animity:
                verbal_animity = self.clause.verb.get_script_animity_for(structure.name)
                if referenced_entity.animity_matches(verbal_animity):
                    pronoun.msi["animity"] = Animity.most_specific(verbal_animity,referenced_entity.msi["animity"])
                    pronoun.add_coreference(referenced_entity)
            else:
                pronoun.add_coreference(referenced_entity)

    def pronouns_in_order(self):
        clause = self.clause
        pronouns_with_structure = []
        for syn_structure in clause.syntactic_structures:
            valid_pronouns = self.only_valid_pronouns(syn_structure.all_entities())
            for valid_pronoun in valid_pronouns:
                pronouns_with_structure.append((valid_pronoun, syn_structure))

        ordered = sorted(pronouns_with_structure,
                         key=lambda (pronoun, structure): clause.index_of(pronoun, True))
        return ordered

    def only_valid_pronouns(self, entities):
        is_valid_personal_pronoun = lambda entity: entity.category() == "pronoun" \
                                                   and entity.msi["type"] == "personal" \
                                                   and entity.msi["person"] == 3 \
                                                   and entity.msi["case"] in [None, "acusative"]

        is_valid_indefinite_pronoun = lambda entity: entity.category() == "pronoun" \
                                                     and entity.msi["type"] == "indefinite" \
                                                     and entity.lexical_form.lower() in ["ambos", "ambas"]

        valid_pronouns = filter(lambda entity: is_valid_personal_pronoun(entity)
                                               or is_valid_indefinite_pronoun(entity),
                                entities)
        return valid_pronouns