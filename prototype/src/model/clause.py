#-*- coding: utf-8 -*-

class Clause:
    def __init__(self, node):
        self.node = node
        self.proper_by_original = {}

        self.children = []
        self.father = None

        self.voice = None

        self.entities = []
        self.relative_entity = None

        self.verb = None
        self.syntactic_structures = []

    def entity_by_original(self, node):
        proper_node = self.proper_by_original[node]
        entities = filter(lambda entity: entity.node == proper_node, self.entities)
        return entities[0]

    def proper_tree(self):
        return self.proper_by_original[self.node]

    def is_relative(self):
        root = self.proper_tree()
        leaves = root.leaves()
        return root.label in [ "subord", "subord-rel" ] and \
            bool(filter(lambda leaf: leaf.msi["category"] == "pronoun" and leaf.msi["type"] == "relative", leaves))

    def is_gerund(self):
        return self.verb.msi["mode"] == "gerundio"

    def has_structure(self, name):
        return name in [ structure.name for structure in self.syntactic_structures ]

    def structure(self, name):
        return filter(lambda structure: structure.name == name, self.syntactic_structures)[0]

    def subord_entities_closest_to_verb_at(self, side, allowed_distance, which_node = lambda node: True):
        which = lambda entity, node: entity.is_subordinated() and entity.highest_subordinating_node() == node \
                    and which_node(node)
        entities_with_node = self.to_entities_with_node(self.nodes_closest_to_verb_at(side, allowed_distance), which)
        return self.grouped_by_node(entities_with_node)

    def verb_level_entities(self):
        by_component = zip(*self.to_entities_with_node(self.verb_level_nodes(), entities = self.entities))
        return list(by_component[0]) if by_component else []

    def entities_closest_to_verb_at(self, side, allowed_distance = float("inf")):
        by_component = zip(*self.to_entities_with_node(self.nodes_closest_to_verb_at(side, allowed_distance)))
        entities = list(by_component[0]) if by_component else []
        return entities

    def lonely_entities(self):
        assigned_entities = sum([ structure.entities for structure in self.syntactic_structures ], [])
        return [ entity for entity in self.entities if entity not in assigned_entities
                and not any([ assigned.contains(entity) for assigned in assigned_entities ]) ]

    def grouped_by_node(self, entities_with_node):
        entities = []
        last_node = None
        for entity, node in entities_with_node:
            if last_node == node:
                entities[-1].append(entity)
            else:
                entities.append([ entity ])
            last_node = node
        return entities

    def to_entities_with_node(self, nodes, which = lambda entity, node: entity.node == node, entities = None):
        if not entities: entities = self.lonely_entities()

        entities_with_node = []
        for node in nodes:
            entities_with_node.extend( (entity, node) for entity in entities if which(entity, node) )
        return entities_with_node

    def verb_level_nodes(self):
        verb_node = self.verb.node
        return verb_node.father.children

    def nodes_closest_to_verb_at(self, side, allowed_distance = float("inf")):
        verb = self.verb.node
        nodes_with_position = [ (verb.absolute_distance_to(node), node) for node in self.verb_level_nodes()
                                  if verb.position_of(node) == side]
        closest = self.sorted_by_closest(nodes_with_position, allowed_distance)
        return [ node for position, node in closest ]  # @UnusedVariable

    def sorted_by_closest(self, things_with_position, allowed_distance):
        return sorted(filter(lambda (position, entity): position <= allowed_distance, things_with_position))

    def set_father(self, clause):
        self.father = clause

    def add_child(self, clause):
        self.children.append(clause)

    def proper_leaves(self):
        return self.proper_tree().leaves()

    def __repr__(self):
        return " ".join([ str(leaf)for leaf in self.proper_leaves()])