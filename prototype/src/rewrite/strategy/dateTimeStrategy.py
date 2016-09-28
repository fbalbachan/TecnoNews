# -*- coding: utf-8 -*-
from src.rewrite.rewrite import Rewrite
from src.utils.collectionUtils import dict_by
from src.utils.stringUtils import set_first_letter_case
from src.utils.fact_time_utils import FactTimeUtils
import datetime

class DateTimeStrategy:
    def __init__(self, ontology):
        self.ontology = ontology
        self.time_utils = FactTimeUtils()
        self.forbidden_words = ["por", "hasta", "entre"]

    def applies_to(self, sentence, node):
        return any((self.applies_to_clause(clause) for clause in sentence.clauses_of_level(0)))

    def rewrite(self, sentence, node):
        # Select first, because the others sometimes are garbage
        clause = [clause for clause in sentence.clauses_of_level(0) if self.applies_to_clause(clause)][0]
        return self.rewrite_clause(clause)

    def applies_to_clause(self, clause):
        clause_own_time = self.time_utils.extract_data_info(clause)
        clause_timebox = self.time_utils.get_timebox(clause)
        clause_timebox_words = clause_timebox.lower().split()
        if len(clause_timebox_words) == 0:
            return False

        for a_forbidden_word in self.forbidden_words:
            if a_forbidden_word == clause_timebox_words[0]:
                return False
        #time_reference = self.time_utils.normalize_datainfo(clause_own_time)
        #clause_timebox = self.time_utils.get_timebox(clause)
        #print self.time_utils.parse_relative_time_info(clause_timebox, time_reference)
        return bool(clause.time_references) and self.time_utils.date_has_info(clause_own_time)

    def rewrite_clause(self, clause):
        grouped = self.grouped_references_for(clause)
        groups_with_position = [(group, self.position_of(group, clause)) for group in grouped]

        source_leaves = self.source_leaves_for(clause)

        text = self.compose_text_for(source_leaves, groups_with_position, clause)
        return Rewrite(clause.node, text)

    def compose_text_for(self, source_leaves, groups, clause):
        first_leaf_lf = clause.proper_leaves()[0].original_lexical_form
        text = ""

        clause_own_time = self.time_utils.extract_data_info(clause)
        normalized_time =  self.time_utils.normalize_datainfo(clause_own_time)
        now = datetime.datetime.now()

        if normalized_time["year"] is not None and normalized_time["year"] - now.year != 0:
            difference = normalized_time["year"] - now.year
            if difference < 0:
                text += "Hace " + str(difference*(-1))
            else:
                text += "En " + str(difference)

            text += " año"
            if abs(difference) > 1:
                text += "s"
            text += ", "
        elif normalized_time["month"] is not None and normalized_time["month"] - now.month != 0:
            difference = normalized_time["month"] - now.month
            if difference < 0:
                text += "Hace " + str(difference*(-1))
            else:
                text += "En " + str(difference)

            text += " mes"
            if abs(difference) > 1:
                text += "es"
            text += ", "
        elif normalized_time["day"] is not None and normalized_time["day"] - now.day != 0:
            difference = normalized_time["day"] - now.day
            if difference < 0:
                text += "Hace " + str(difference*(-1))
            else:
                text += "En " + str(difference)

            text += " día"
            if abs(difference) > 1:
                text += "s"
            text += ", "

        #groups_by_pos = dict_by(groups, lambda (group, position): position)

        #middle_end_groups = sum([[group for group, pos in groups_by_pos[pos]] for pos in ["middle", "end"]
        #                         if pos in groups_by_pos], [])

        ##if middle_end_groups:
        ##    text += set_first_letter_case(first_leaf_lf, self.text_for(middle_end_groups, True))

        #last_is_dot = source_leaves[-1].lexical_form == "."
        #middle_leaves = source_leaves if not last_is_dot else source_leaves[:-1]

        #middle_text = self.with_adjusted_case(" ".join([leaf.joined_text() for leaf in middle_leaves]), source_leaves[0])

        #if not text:
        #    middle_text = set_first_letter_case(first_leaf_lf, middle_text)
        #text += middle_text

        #if "start" in groups_by_pos:
        #    groups = [group for group, pos in groups_by_pos["start"]]
        #    text += self.text_for(groups, False)

        #text = text.replace(" ,", ",").replace(" .", ".")

        #if last_is_dot:
        #    text += "."
        text += self.with_adjusted_case(first_leaf_lf, clause.proper_leaves()[0])
        text += " " + " ".join([str(leaf) for leaf in clause.proper_leaves()[1:]])
        text = text.replace("_", " ")

        return text

    def with_adjusted_case(self, text, leaf):
        if leaf.msi["category"] == "noun" and leaf.msi["type"] == "proper":
            return set_first_letter_case(leaf.original_lexical_form, text)
        else:
            return text[0].lower() + text[1:]

    def text_for(self, groups, at_start):
        text = ""
        for group in groups:
            all_leaves = sum([ self.filter_not_punctuation(node.leaves()) for node in group ], [])
            text_of_group = " ".join([ leaf.joined_text() for leaf in all_leaves])
            text += (text_of_group + ", ") if at_start else \
                (", " + self.with_adjusted_case(text_of_group, group[0].leaves()[0]))

        return text

    def source_leaves_for(self, clause):
        commas = []
        for node in clause.time_references:
            leaf = node.leaves()[0]
            index = clause.proper_leaves().index(leaf)
            if index > 0:
                previous = clause.proper_leaves()[index - 1]
                if previous.msi["category"] == "punctuation" and previous.msi["type"] == ",":
                    commas.append(previous)

        datetime_leaves = sum([node.leaves() for node in clause.time_references], commas)
        datetime_leaves = [clause.original_by_proper(leaf) for leaf in datetime_leaves]

        return [leaf for leaf in clause.node.leaves() if leaf not in datetime_leaves]

    def position_of(self, group, clause):
        all_leaves = self.filter_not_punctuation(clause.proper_leaves())
        start_index = all_leaves.index(self.filter_not_punctuation(group[0].leaves())[0])
        end_index = all_leaves.index(self.filter_not_punctuation(group[-1].leaves())[-1])

        if start_index == 0:
            return "start"
        elif end_index == len(all_leaves) - 1:
            return "end"
        else:
            return "middle"

    def grouped_references_for(self, clause):
        grouped = []
        group = []

        for reference in clause.time_references:
            if not group or self.are_adjacent(group[-1], reference, clause):
                group.append(reference)
            else:
                grouped.append(group)
                group = [reference]

        if group:
            grouped.append(group)

        return grouped

    def filter_not_punctuation(self, leaves):
        return filter(lambda leaf: leaf.msi["category"] != "punctuation", leaves)

    def are_adjacent(self, node, other, clause):
        all_leaves = filter(lambda leaf: leaf.msi["category"] != "punctuation", clause.proper_leaves())
        node_leaves = self.filter_not_punctuation(node.leaves())
        other_leaves = self.filter_not_punctuation(other.leaves())
        return all_leaves.index(node_leaves[-1]) == all_leaves.index(other_leaves[0]) - 1

    type = "dislocation"
