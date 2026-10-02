# -*- coding: utf-8 -*-
from src.model.entity.entity import Entity
from src.model.entity.entityMSISeer import EntityMSISeer
from src.parser.parseNode import ParseNode


class EntityExtractor:

    def __init__(self, clause, global_context={}):
        global debug_mode
        debug_mode = False

        self.clause = clause
        self.global_context = global_context

    def extract(self):
        if debug_mode: print("--> EntityExtractor.extract()")

        root = self.clause.proper_tree()
        entity_nodes = self.nodes_from_entity_labels(root) + \
                       self.infinitive_structures() + \
                       self.relative_abnormal_nodes()

        entities = self.entities_for(entity_nodes)
        entities = sorted(entities, key=lambda entity: entity.node.level(), reverse=True)
        entities = self.remove_invalid_coordinated(entities)

        self.assign_msi(entities)

        EntityExtractor.compute_proper_tree_for(entities)

        return entities

    def nodes_from_entity_labels(self, root):
        sn_entity_nodes = root.nodes_with_labels(["sn"])
        sn_entity_nodes = [p_node for p_node in sn_entity_nodes if not p_node.has_child_with_label("numero")]

        other_entity_nodes = root.nodes_with_labels(["patons", "ptonic", "coor-n"])
        return sn_entity_nodes + other_entity_nodes

    @staticmethod
    def compute_proper_tree_for(entities):
        if debug_mode: print("--> EntityExtractor.compute_proper_tree_for(entities): ", entities)
        for entity in entities:
            original = entity.node
            foreign_nodes = [child.node for child in entity.children]
            entity.proper_node = original.cloned_by_original(foreign_nodes)[entity.node]

    def remove_invalid_coordinated(self, entities):
        return [entity for entity in entities if not (entity.node.label == "coor-n" and len(entity.children) == 1)]

    def entities_for(self, nodes, attributes=[]):
        entities_by_node = {}

        by_level = ParseNode.by_level(nodes)

        for level, nodes in sorted(by_level.items()):  # @UnusedVariable
            for node in nodes:
                if self.starts_with_lo(node):
                    continue

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

        return list(entities_by_node.values())

    def starts_with_lo(self, node):
        first_leaf = node.leaves()[0]

        match = first_leaf.label_lemma_lf_matches(None, ["el"], ["lo", "Lo"]) \
                and len(node.leaves()) == len(node.children)

        return match

    def assign_msi(self, entities):
        if debug_mode: print("--> EntityExtractor.assign_msi(entities): ", entities)
        entity_msi_seer = EntityMSISeer(global_context=self.global_context)
        for entity in entities:
            entity.msi = entity_msi_seer.msi_of(entity)

    def relative_abnormal_nodes(self):
        desired_labels = ["grup-nom-ms", "grup-nom-fs", "grup-nom-mp", "grup-nom-fp"]
        root = self.clause.proper_tree()

        return [node for node in root.nodes_with_labels(desired_labels) if node.father.subordinates_others()]

    def infinitive_structures(self):
        clause = self.clause
        root = clause.proper_tree()
        return root.nodes_with_labels(["grup-verb-inf"])

    attributes_by_label = \
        {
            "grup-verb-inf": [("infinitive", None)],
            "coor-n": [("coordinated", None)]
        }
