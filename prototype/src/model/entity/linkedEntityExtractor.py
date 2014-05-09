#-*- coding: utf-8 -*-
from src.ling.tacit_subjects import somebody


class LinkedEntityExtractor:

    def __init__(self, clause):
        self.clause = clause

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

        entity = None
        if brothers_at_left:
            entity = father.entity_by_original(brothers_at_left[0])
        if not entity: entity = self.extract_from_relative()
        return entity

    def extract_from_relative(self):
        clause = self.clause
        if not clause.is_root():
            father = clause.father
            entity_node = clause.node.father
            return father.entity_by_original(entity_node)
        return None