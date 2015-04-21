# -*- coding: utf-8 -*-
from src.model.entity.tacitEntity import TacitEntity
from src.model.entity.animity_enum import AnimityEnum
from src.ling.gender_enum import GenderEnum
from src.ling.number_enum import NumberEnum
from src.model.syntax.syntacticAnalyzer import SyntacticAnalyzer


class RelativePronounSolver:
    def __init__(self, clause):
        self.clause = clause
        self.linker = clause.relative_linker

    def solve(self):
        clause = self.clause

        if self.is_possessive_relative():
            self.solve_possessive_relative()

        elif self.is_undefined_relative():
            self.solve_undefined_relative()

        elif self.is_valid_linker():
            solve_method_by_voice = {"active":  self.solve_active_voice,
                                     "passive": self.solve_passive_voice}
            solve_method_by_voice[clause.voice]()

    def is_undefined_relative(self):
        linker_words = [leaf.lexical_form for leaf in self.linker]
        return linker_words == ["lo", "cual"]

    def solve_undefined_relative(self):
        clause = self.clause
        clause.relative_entity = None

        destination_by_voice = {"active": "subject",
                                "passive": "od"}
        destination = clause.structure(destination_by_voice[clause.voice])

        msi = {"category": "pronoun",  "type": "demonstrative",
               "gender":   "neutral",  "person": 3,
               "number":   "singular", "case": None,
               "semantic_classification": None}
        undefined_pronoun = TacitEntity("eso", msi)

        destination.append(undefined_pronoun)

    def is_possessive_relative(self):
        pronoun = self.linker[0].lexical_form
        return pronoun in ["cuyo", "cuya", "cuyos", "cuyas"]

    def solve_possessive_relative(self):
        clause = self.clause
        possessed_entity = clause.sorted(clause.lonely_entities(), False)[0]
        possessed_entity.owner = clause.relative_entity

        destination_by_voice = {"active": "subject",
                                "passive": "od"}

        destination_name = destination_by_voice[clause.voice]
        destination = clause.structure(destination_name)

        if AnimityEnum.animities_match(possessed_entity.msi["animity"],
                                   clause.verb.get_script_animity_for(destination_name)):
            possessed_entity.msi["animity"] = \
                AnimityEnum.most_specific(possessed_entity.msi["animity"],
                                          clause.verb.get_script_animity_for(destination_name))
            possessed_entity.owner.msi["animity"] = possessed_entity.msi["animity"]
            destination.append(possessed_entity)

    def is_valid_linker(self):
        word = self.linker[0].lexical_form
        is_valid = word not in ["donde", "adonde"]
        return is_valid

    def solve_active_voice(self):
        clause = self.clause
        gender = clause.try_to_get_gender_from_relative_linker()
        number = clause.try_to_get_number_from_relative_linker()
        is_quien_relative = clause.is_quien_relative()

        found = False
        for destination in self.possible_entity_structures():
            if found:
                break

            if not clause.has_structure(destination):
                continue

            include_myself = True
            structure = clause.structure(destination)
            verb_animity = clause.verb.get_script_animity_for(destination)

            nested_entities = clause.relative_entity.get_nested_entities(include_myself)
            for nested_relative_entity in nested_entities:

                if not RelativePronounSolver.relative_entity_matches_msi(nested_relative_entity,
                                                                         is_quien_relative,
                                                                         gender, number, verb_animity):
                    continue

                if structure.is_empty() or structure.is_multiple():
                    if is_quien_relative:
                        nested_relative_entity.msi["animity"] = AnimityEnum.animated

                    nested_relative_entity.msi["animity"] = AnimityEnum.most_specific(verb_animity,
                                                                                  nested_relative_entity.msi["animity"])
                    structure.entities.append(nested_relative_entity)
                    found = True
                    break

                entity = structure.entity()
                if entity.matches(nested_relative_entity) and entity.is_tacit():
                    if is_quien_relative:
                        nested_relative_entity.msi["animity"] = AnimityEnum.animated

                    nested_relative_entity.msi["animity"] = \
                        AnimityEnum.most_specific(verb_animity, nested_relative_entity.msi["animity"])

                    structure.replace(entity, nested_relative_entity)
                    found = True
                    break

        else:
            self.update_msi_of_default_entity(clause)

    @staticmethod
    def relative_entity_matches_msi(relative_entity, is_quien_relative, gender, number, verb_animity):
        matches_animity = (not is_quien_relative or relative_entity.animity_matches(AnimityEnum.animated)) \
                          and relative_entity.animity_matches(verb_animity)
        matches_gender = not gender or relative_entity.gender_matches(gender)
        matches_number = not number or relative_entity.number_matches(number)
        matches_msi = matches_gender and matches_number and matches_animity
        return matches_msi

    def update_msi_of_default_entity(self, clause):
        for destination in self.possible_entity_structures():
            if clause.has_structure(destination):
                structure = clause.structure(destination)
                if not structure.is_empty():
                    entity = structure.entity()
                    if clause.is_quien_relative():
                        entity.msi["animity"] = AnimityEnum.animated
                        gender = clause.try_to_get_gender_from_relative_linker()
                        if gender:
                            entity.msi["gender"] = GenderEnum.most_specific(gender, entity.msi["gender"])
                        number = clause.try_to_get_number_from_relative_linker()
                        if number:
                            entity.msi["number"] = NumberEnum.most_specific(number, entity.msi["number"])
                    break

    def possible_entity_structures(self):
        first_linker_leaf = self.linker[0]
        first_linker_category = first_linker_leaf.msi["category"]

        if first_linker_category == "adposition":
            structures = ["regimen"]
            if first_linker_leaf.lexical_form in SyntacticAnalyzer.instrument_goal_preps:
                structures.append("instrument_goal")

            structures.append("adjuncts")
            if first_linker_leaf.lexical_form == "a":
                structures = ["od"] + structures

        else:
            structures = ["subject", "od"]

        return structures

    def solve_passive_voice(self):

        clause = self.clause
        is_quien = clause.is_quien_relative()
        gender = clause.try_to_get_gender_from_relative_linker()
        number = clause.try_to_get_number_from_relative_linker()

        destination_by_preposition = {"por": "subject",
                                      "con": "instrument_goal"}

        first_linker_word = self.linker[0].lexical_form

        if first_linker_word in destination_by_preposition:
            destination = destination_by_preposition[first_linker_word]
        else:
            destination = "od"

        structure = clause.structure(destination)
        include_myself = True
        nested_entities = clause.relative_entity.get_nested_entities(include_myself)
        verb_animity = clause.verb.get_script_animity_for(destination)

        for nested_relative_entity in nested_entities:
            if gender and not nested_relative_entity.gender_matches(gender) \
                    or number and not nested_relative_entity.number_matches(number) \
                    or is_quien and not nested_relative_entity.animity_matches(AnimityEnum.animated) \
                    or not nested_relative_entity.animity_matches(verb_animity):
                continue

            if structure.accept(nested_relative_entity):
                structure.tacit_entities = []
                structure.entities = []
                if is_quien:
                    nested_relative_entity.msi["animity"] = AnimityEnum.animated
                structure.append(nested_relative_entity)
                break
        else:
            if not structure.is_empty() and is_quien:
                entity = structure.entity()
                entity.msi["animity"] = AnimityEnum.animated

    @staticmethod
    def guess_linker_leaves(clause):
        leaves = clause.proper_tree().leaves()
        linker = []

        # Parche por bug de freeling (ej. 'con la que')
        last_leaf_of_relative = clause.relative_entity.leaves()[-1]
        if last_leaf_of_relative.msi["category"] == "adposition":
            linker.append(last_leaf_of_relative)

        category_sequences = [["adposition", "determinant", "pronoun"],
                              ["adposition", "pronoun"]]

        for category_sequence in category_sequences:
            while category_sequence:
                arranged = zip(category_sequence, leaves)

                initial_leaves_match_category_seq = \
                    all([leaf.msi["category"] == expected_category for (expected_category, leaf) in arranged])

                if initial_leaves_match_category_seq:
                    category_sequence = []
                    linker.extend(zip(*arranged)[1])
                else:
                    category_sequence = category_sequence[1:]

            if linker:
                break

        return linker