#-*- coding: utf-8 -*-
from src.model.entity.entity import Entity
from src.model.entity.entityMSISeer import EntityMSISeer
from src.parser.parseNode import ParseNode

class EntityExtractor:

    def __init__(self, clause):
        self.clause = clause

    def extract(self):
        root = self.clause.proper_tree()
        entity_nodes = root.nodes_with_labels(self.entity_labels) + self.verb_level_infinitive_structures()

        entities = self.entities_for(entity_nodes)
        entities = sorted(entities, key = lambda entity: entity.node.level(), reverse = True)
        entities = self.remove_invalid_coordinated(entities)

        self.assign_msi(entities)

        return entities

    def remove_invalid_coordinated(self, entities):
        return filter(lambda entity: not (entity.node.label == "coor-n" and len(entity.children) == 1), entities)

    def entities_for(self, nodes):
        entities_by_node = {}

        by_level = ParseNode.by_level(nodes)
        level_parents = set()

        for level, nodes in sorted(by_level.items()):  # @UnusedVariable
            for node in nodes:
                entity = Entity(node)
                entities_by_node[node] = entity

                parents = filter(lambda node: node in level_parents, node.path_to_root())
                if parents:
                    parent = parents[0]
                    father = entities_by_node[parent]
                    entity.father = father
                    father.children.append(entity)
            level_parents = set(nodes)

        return entities_by_node.values()

    def assign_msi(self, entities):
        entity_msi_seer = EntityMSISeer()
        for entity in entities: entity.msi = entity_msi_seer.msi_of(entity)

    def verb_level_infinitive_structures(self):
        clause = self.clause
        root = clause.proper_tree()
        desired_level = clause.verb.level() if clause.voice else 1
        return filter(lambda node: node.level() == desired_level, root.nodes_with_labels(["grup-verb-inf"]))

    entity_labels = ["sn", "patons", "ptonic", "coor-n"]