# -*- coding: utf-8 -*-
from src.model.entity.entity import Entity
from src.model.entity.entityMSISeer import EntityMSISeer
from src.parser.parseNode import ParseNode


class EntityExtractor:

    def __init__(self, clause):
        self.clause = clause

    def extract(self):
        # print "Entering EntityExtractor.extract()"
        root = self.clause.proper_tree()
        entity_nodes = root.nodes_with_labels(self.entity_labels) + self.infinitive_structures() + \
            self.relative_abnormal_nodes()

        entities = self.entities_for(entity_nodes)
        entities = sorted(entities, key=lambda entity: entity.node.level(), reverse=True)
        entities = self.remove_invalid_coordinated(entities)

        self.assign_msi(entities)
        EntityExtractor.compute_proper_tree_for(entities)

        return entities

    @staticmethod
    def compute_proper_tree_for(entities):
        for entity in entities:
            original = entity.node
            foreign_nodes = [child.node for child in entity.children]
            entity.proper_node = original.cloned_by_original(foreign_nodes)[entity.node]

    def remove_invalid_coordinated(self, entities):
        return filter(lambda entity: not (entity.node.label == "coor-n" and len(entity.children) == 1), entities)

    def entities_for(self, nodes, attributes=[]):
        entities_by_node = {}

        by_level = ParseNode.by_level(nodes)

        for level, nodes in sorted(by_level.items()):  # @UnusedVariable
            for node in nodes:
                entity = Entity(node)

                label = node.label
                if label in self.attributes_by_label:
                    entity.attributes.update(self.attributes_by_label[label])

                entity.attributes.update(attributes)
                entities_by_node[node] = entity

                # Update entity object with parent/child relations
                for parent in node.path_to_root():
                    parent_level = parent.level()
                    if parent_level in by_level and parent in by_level[parent.level()]:
                        father = entities_by_node[parent]
                        entity.father = father
                        father.children.append(entity)

        return entities_by_node.values()

    def assign_msi(self, entities):
        # print "Entering assign_msi"
        entity_msi_seer = EntityMSISeer()
        for entity in entities:
            entity.msi = entity_msi_seer.msi_of(entity)

    def relative_abnormal_nodes(self):
        desired_labels = ["grup-nom-ms", "grup-nom-fs", "grup-nom-mp", "grup-nom-fp"]
        root = self.clause.proper_tree()

        return filter(lambda node: node.father.subordinates_others(),
                      root.nodes_with_labels(desired_labels))

    def infinitive_structures(self):
        clause = self.clause
        root = clause.proper_tree()
        return root.nodes_with_labels(["grup-verb-inf"])

    attributes_by_label = {"grup-verb-inf": [("infinitive", None)], "coor-n": [("coordinated", None)]}

    entity_labels = ["sn", "patons", "ptonic", "coor-n"]