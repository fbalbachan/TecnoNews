#-*- coding: utf-8 -*-

class LinkedEntityExtractor:

    def __init__(self, clause, context):
        self.clause = clause
        self.context = context

    def extract(self):
        extract_methods_by_label = {"subord" : self.extract_from_non_relative,
                                    "subord-rel" : self.extract_from_relative }

        root_label = self.clause.proper_tree().label
        return extract_methods_by_label[root_label]()

    def extract_from_non_relative(self):
        clause = self.clause
        father = clause.father

        root = clause.node
        brothers = root.father.children
        brothers_at_left = brothers[:brothers.index(root)]

        return father.entity_by_original(brothers_at_left[0])

    def extract_from_relative(self):
        clause = self.clause
        father = clause.father
        entity_node = clause.node.father
        return father.entity_by_original(entity_node)
