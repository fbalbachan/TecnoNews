#-*- coding: utf-8 -*-
from re import match

from src.utils.resources import instance as resources


class DateTimeFinder:
    def __init__(self, clause):
        self.clause = clause

    def find(self):
        clause = self.clause
        useful_nodes = clause.verb_level_nodes() if clause.voice else clause.proper_tree().children
        nodes = filter(lambda node: not node.is_leaf() and \
                       (self.has_data(node) or self.is_valid_subord(node)), useful_nodes)
        return nodes

    def is_valid_subord(self, node):
        if node.label != "grup-sp": return False
        return any(( check(node) for check in [ self.has_year, self.is_en_plus_num, self.has_time_word ]))

    def has_year(self, node):
        return any( ( match("^[12]\d{3}$", each.lexical_form) for each in node.leaves_of_category("number")) )

    def is_en_plus_num(self, node):
        leaves = node.leaves()
        return len(leaves) == 2 and leaves[0].lemma == "en" and leaves[1].msi["category"] == "number"

    def has_data(self, node):
        return "data" in [ each.label for each in node if not each.is_leaf() ]

    def has_time_word(self, node):
        return bool({ leaf.lemma for leaf in node.leaves() } & self.time_words)

    time_words = { word.lower() for word in resources.parse_csv_in("syntax", "time_words") }