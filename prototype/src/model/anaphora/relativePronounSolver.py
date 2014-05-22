# -*- coding: utf-8 -*-
from src.model.entity.tacitEntity import TacitEntity

class RelativePronounSolver:
    def __init__(self, clause):
        self.clause = clause
        self.linker = clause.relative_linker

    def solve(self):
        clause = self.clause

        if self.is_possesive_relative():
            self.solve_possesive_relative()
        elif self.is_undefined_relative():
            self.solve_undefined_relative()
        elif self.is_valid_linker():
            solve_method_by_voice = { "active" : self.solve_active_voice, "passive" : self.solve_passive_voice }
            solve_method_by_voice[clause.voice]()

    def is_undefined_relative(self):
        linker_words = [ leaf.lexical_form for leaf in self.linker ]
        return linker_words == ["lo", "cual"]

    def solve_undefined_relative(self):
        clause = self.clause
        clause.relative_entity = None

        destination_by_voice = { "active" : "subject", "passive" : "od" }
        destination = clause.structure(destination_by_voice[clause.voice])

        msi = { "category" : "pronoun", "type" : "demostrative", "gender" : "neutral", "person" : 3,
               "number" : "singular", "case" : None}
        undefined_pronoun = TacitEntity("eso", msi)

        destination.append(undefined_pronoun)

    def is_possesive_relative(self):
        pronoun = self.linker[0].lexical_form
        return pronoun in [ "cuyo", "cuya", "cuyos", "cuyas" ]

    def solve_possesive_relative(self):
        clause = self.clause
        possessed_entity = clause.sorted(clause.lonely_entities(), False)[0]
        possessed_entity.owner = clause.relative_entity

        destination_by_voice = { "active" : "subject", "passive" : "od" }
        destination = clause.structure(destination_by_voice[clause.voice])
        destination.append(possessed_entity)

    def is_valid_linker(self):
        word = self.linker[0].lexical_form
        return word not in [ "donde", "adonde" ]

    def solve_active_voice(self):
        clause = self.clause
        for destination in self.possible_entity_structures():
            if not clause.has_structure(destination): continue
            structure = clause.structure(destination)
            if structure.is_empty():
                structure.entities.append(clause.relative_entity)
                break
            else:
                entity = structure.entity()
                if entity.matches(clause.relative_entity) and entity.is_tacit():
                    structure.replace(entity, clause.relative_entity)
                    break

    def possible_entity_structures(self):
        first_linker_leaf = self.linker[0]
        first_linker_category = first_linker_leaf.msi["category"]

        if first_linker_category == "adposition":
            structures = [ "regimen", "adjuncts" ]
            if first_linker_leaf.lexical_form.lower() == "a": structures = [ "od" ] + structures
        else:
            structures = [ "subject" , "od" ]
        return structures

    def solve_passive_voice(self):
        clause = self.clause
        destination_by_preposition = { "por" : "subject", "con" : "adjuncts" }
        first_linker_word = self.linker[0].lexical_form

        destination = destination_by_preposition[first_linker_word] if first_linker_word in destination_by_preposition\
            else "od"

        structure = clause.structure(destination)
        entity = clause.relative_entity
        if structure.accept(entity):
            structure.tacit_entities = []
            structure.entities = [ clause.relative_entity ]

    @staticmethod
    def guess_linker_leaves(clause):
        leaves = clause.proper_tree().leaves()
        linker = []
        last_leaf_of_relative = clause.relative_entity.leaves()[-1] # Parche por bug de freeling (ej. 'con la que')
        if last_leaf_of_relative.msi["category"] == "adposition": linker.append(last_leaf_of_relative)

        category_sequences = [ [ "adposition", "determinant", "pronoun" ], [ "adposition", "pronoun" ] ]
        for category_sequence in category_sequences:
            while category_sequence:
                arranged = zip(category_sequence, leaves)
                if all([ leaf.msi["category"] == expected_category for (expected_category, leaf) in arranged ]):
                    category_sequence = []
                    linker.extend(zip(*arranged)[1])
                else:
                    category_sequence = category_sequence[1:]
            if linker: break
        return linker