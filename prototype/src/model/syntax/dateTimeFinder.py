# -*- coding: utf-8 -*-
from re import match

from src.utils.resources import instance as resources


class DateTimeFinder:
    def __init__(self, clause):
        self.clause = clause

    def find(self):
        clause = self.clause
        useful_nodes = clause.verb_level_nodes() if clause.voice else clause.proper_tree().children
        time_nodes = [node for node in useful_nodes if not node.is_leaf() and (self.has_data(node)
                                                                 or self.is_valid_subord(node)
                                                                 or self.is_valid_sadv(node))]
        return time_nodes

    def is_valid_sadv(self, node):
        return node.label == "sadv" and node.nodes_with_labels("sn-tmp")

    def is_valid_subord(self, node):
        time_reference_checks = (check(node) for check in [self.has_year,
                                                           self.is_en_plus_num,
                                                           DateTimeFinder.has_time_word])
        return any(time_reference_checks)

    def has_year(self, node):
        first_leaf = node.leaves()[0]
        year_regexp = r"^1\d{3}$|^2[012]\d{2}$"  # 1xxx or 20xx or 21xx or 22xx
        year_matches = [each.father.label == "numero"
                        and match(year_regexp, each.lexical_form) for each in node.leaves_of_category("number")]

        return first_leaf.msi["category"] == "adposition" \
               and first_leaf.lexical_form not in self.non_temporal_adpositions \
               and any(year_matches)

    def is_en_plus_num(self, node):
        leaves = node.leaves()

        return len(leaves) == 2 \
               and leaves[0].lemma == "en" \
               and leaves[1].msi["category"] == "number"

    def has_data(self, node):
        first_leaf = node.leaves()[0]
        node_labels = [each.label for each in node if not each.is_leaf()]
        is_temporal_adposition = first_leaf.lexical_form not in self.non_temporal_adpositions

        return is_temporal_adposition and "data" in node_labels

    @staticmethod
    def has_time_word(node):
        lemmas_in_leaves = {leaf.lemma for leaf in node.leaves()}
        time_lemmas_in_leaves = lemmas_in_leaves & DateTimeFinder.time_words
        return bool(time_lemmas_in_leaves)

    time_words = {word.lower() for word in resources.parse_csv_in("syntax", "time_words")}

    non_temporal_adpositions = ["contra", "a", "ante", "bajo", "sin", "según", "tras", "a_causa_de"]
