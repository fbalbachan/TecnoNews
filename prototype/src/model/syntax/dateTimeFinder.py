#-*- coding: utf-8 -*-
from src.utils.resources import instance as resources

class DateTimeFinder:
    def __init__(self, clause):
        self.clause = clause

    def find(self):
        clause = self.clause
        useful_nodes = clause.verb_level_nodes() if clause.voice else clause.proper_tree().children
        nodes = filter(lambda node: not node.is_leaf() and \
                       (node.label == "data" or (node.label == "grup-sp" and self.has_time_word(node))), useful_nodes)
        return nodes

    def has_time_word(self, node):
        return bool({ leaf.lexical_form for leaf in node.leaves() } & self.time_words)

    time_words = { word.lower() for word in resources.parse_csv_in("syntax", "time_words") }