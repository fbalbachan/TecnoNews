#-*- coding: utf-8 -*-
from src.model.linkedEntity import LinkedEntity

class PersonalPronounSolver:
    def __init__(self, clause, context):
        self.clause = clause
        self.context = context

    def solve(self):
        clause = self.clause

        for structure in clause.syntactic_structures:
            pronouns = filter(self.is_valid_pronoun, structure.all_entities())
            for pronoun in pronouns:
                self.link(clause, structure, pronoun)

    def is_valid_pronoun(self, entity):
        is_personal_pronoun = lambda entity: entity.category() == "pronoun" and entity.msi["type"] == "personal" \
            and entity.msi["person"] == 3 and entity.msi["case"] == None
        is_valid_demostrative_pronoun = lambda entity: entity.category() == "pronoun" \
            and entity.msi["type"] == "demostrative" and entity.lexical_form.lower() not in [ "eso", "esto", "aquello" ]
        return is_personal_pronoun(entity) or is_valid_demostrative_pronoun(entity)

    def link(self, clause, structure, entity):
        referenced_entity = self.search_referenced_entity_for(entity)
        if referenced_entity:
            linked_entity = LinkedEntity(entity, referenced_entity)
            structure.replace(entity, linked_entity)
            clause.linked_entities.append(linked_entity)

    def search_referenced_entity_for(self, actual_entity):
        previous_sentences = self.context["sentences"]
        if not previous_sentences: return None
        selected_sentences = previous_sentences[::-1][0:3]

        for sentence in selected_sentences:
            entity = self.search_referenced_entity_in(sentence, actual_entity)
            if entity: return entity
        return None

    def search_referenced_entity_in(self, sentence, actual_entity):
        search_order_by_voice = { "active" : [ "subject", "od", "adjuncts" ],
                                 "passive" : [ "od", "subject", "adjuncts" ],
                                 None : [ "subject" ] }

        clause = sentence.main_clause()
        for structure_name in search_order_by_voice[clause.voice]:
            if not clause.has_structure(structure_name): continue
            structure = clause.structure(structure_name)
            matching_entities = filter(lambda entity: entity.matches(actual_entity), structure.all_entities())
            if matching_entities: return matching_entities[0]
        return None