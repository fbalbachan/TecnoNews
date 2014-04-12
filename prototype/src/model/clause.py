#-*- coding: utf-8 -*-

class Clause:
    def __init__(self, node):
        self.node = node
        self.children = []
        self.father = None
        self.proper_tree = None
        self.voice = None
        self.entities = []
        self.verb = None
        self.syntactic_structures = []

    # Debería ser lonely_verb...
    def verb_level_entities(self):
        return self.select_verb_level_ones_of(self.lonely_entities())

    def verb_level_subord_entities_at(self, side, allowed_distance = float("inf"), which = lambda node: True):
        subord_nodes = filter(which, self.verb_level_subords_at(side, allowed_distance))
        entity_lists = [ [ entity for entity in self.lonely_entities() if node.contains(entity.node) ]
                    for node in subord_nodes]
        return filter(lambda entity_list: entity_list, entity_lists)

    # No me gusta el código duplicado entre esto y lo que hace la misma búsqueda para entidades.
    def verb_level_subords_at(self, side, allowed_distance):
        subords = self.select_verb_level_ones_of(self.proper_tree.nodes_with_labels([ "coor-sp", "grup-sp", "sp-de" ]))
        verb = self.verb.node
        subords_with_position = [ (verb.absolute_distance_to(node), node) for node in subords
                                 if verb.position_of(node) == side]
        closest = self.sorted_by_closest(subords_with_position, allowed_distance)
        return [ node for position, node in closest ]  # @UnusedVariable

    def lonely_entities(self):
        assigned_entities = sum([ structure.entities for structure in self.syntactic_structures ], [])
        return [ entity for entity in self.entities if entity not in assigned_entities
                and not any([ assigned.contains(entity) for assigned in assigned_entities ]) ]

    def select_verb_level_ones_of(self, leveled_objects):
        verb_node = self.verb.node
        verb_level = verb_node.level()
        return filter(lambda thing: thing.level() == verb_level, leveled_objects)

    def entities_closest_to_verb_at(self, side, allowed_distance = float("inf")):
        verb = self.verb.node
        entities_with_position = [ (verb.absolute_distance_to(entity.node), entity)
                                  for entity in self.verb_level_entities()
                                  if verb.position_of(entity.node) == side]

        closest = self.sorted_by_closest(entities_with_position, allowed_distance)
        return [ entity for position, entity in closest ]  # @UnusedVariable

    def sorted_by_closest(self, things_with_position, allowed_distance):
        return sorted(filter(lambda (position, entity): position <= allowed_distance, things_with_position))

    def set_father(self, clause):
        self.father = clause

    def add_child(self, clause):
        self.children.append(clause)

    def proper_leaves(self):
        return self.proper_tree.leaves()

    def __repr__(self):
        return str(self.proper_leaves())