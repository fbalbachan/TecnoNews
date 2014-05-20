# -*- coding: utf-8 -*-

class RelativePronounSolver:
    def __init__(self, clause):
        self.clause = clause
        self.linker = self.guess_linker_leaves()

    def solve(self):
        clause = self.clause

        if self.is_valid_linker():
            solve_method_by_voice = { "active" : self.solve_active_voice, "passive" : self.solve_passive_voice }
            solve_method_by_voice[clause.voice]()


    def is_valid_linker(self):
        linker_words = [ leaf.lexical_form for leaf in self.linker ]
        return linker_words not in [ ["cuyo"], ["cuya"], ["cuyos"], ["cuyas"], ["donde"], ["adonde"], ["lo", "cual"] ]

    def solve_active_voice(self):
        clause = self.clause
        first_linker_category = self.linker[0].msi["category"]

        destinations = [ "regimen", "adjuncts" ] if first_linker_category == "adposition" else [ "subject" , "od" ]

        for destination in destinations:
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

    def guess_linker_leaves(self):
        clause = self.clause
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