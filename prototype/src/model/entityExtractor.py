#-*- coding: utf-8 -*-
from src.model.entity import Entity
from src.model.entityMSISeer import EntityMSISeer

class EntityExtractor:

    def __init__(self, clause):
        self.clause = clause

    def extract(self):
        root = self.clause.proper_tree()
        entity_nodes = root.nodes_with_labels(self.entity_labels) + self.verb_level_infinitive_structures()
        entities = [ Entity(node) for node in entity_nodes ]

        entity_msi_seer = EntityMSISeer()
        for entity in entities: entity.msi = entity_msi_seer.msi_of(entity)
        return entities

    def verb_level_infinitive_structures(self):
        clause = self.clause
        root = clause.proper_tree()
        desired_level = clause.verb.level() if clause.voice else 1
        return filter(lambda node: node.level() == desired_level, root.nodes_with_labels(["grup-verb-inf"]))

    entity_labels = ["sn", "patons", "ptonic", "coor-n"]