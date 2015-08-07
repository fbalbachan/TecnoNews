# -*- coding: utf-8 -*-
from src.ling.gender import Gender
from src.ling.number import Number
from src.model.syntax.dateTimeFinder import DateTimeFinder
from src.parser.leafNode import LeafNode
from src.utils.tree.treeNode import TreeNode

debug_mode = False


class Clause(TreeNode):
    def __init__(self, node):
        TreeNode.__init__(self)

        self.node = node
        self.proper_by_original = {}

        self.voice = None

        self.entities = []
        self.time_references = []
        self.time_entities = []

        self.relative_entity = None
        self.relative_linker = []

        self.verb = None
        self.syntactic_structures = []

        self.global_operators = set()

        self.valuated_adverbs = []
        self.isolated_adjectives = []

        self.attributes = []

    #
    # Questions to the Clause object
    #
    def has_attr(self, attribute):
        return attribute in self.attributes

    def is_fact(self):
        go = self.global_operators
        return not go or go == {"negation"}

    def is_negated(self):
        return self.has_global_operator_of("negation")

    def has_kind_of_cataphoric_structure(self):
        return self.verb.transitivity == "EQUATIVE" and \
               any((child.is_subordinated_with("que") for child in self.children))

    def has_global_operator_of(self, *classes):
        return bool(filter(lambda operator: operator.klass in classes, self.global_operators))

    def is_relative(self):
        root = self.proper_tree()
        leaves = root.leaves()

        relative_pronouns = filter(lambda leaf: leaf.msi["category"] == "pronoun"
                                                and leaf.msi["type"] == "relative",
                                   leaves)

        there_are_relative_pronouns = bool(relative_pronouns)

        return root.label in ["subord", "subord-rel"] and there_are_relative_pronouns

    def is_quien_relative(self):
        if not self.is_relative():
            return False

        is_quien_vector = map(lambda word: word in ["quien", "quienes", "quién", "quiénes"],
                              self.relative_linker_words())
        return any(is_quien_vector)

    def is_cuyo_relative(self):
        if not self.is_relative():
            return False
        is_cuyo_vector = map(lambda word: word in ["cuyo", "cuya", "cuyos", "cuyas"], self.relative_linker_words())
        return any(is_cuyo_vector)

    def is_subordinated_with(self, header_lexical_form):
        return self.is_subordinated_with_any([header_lexical_form])

    def is_subordinated_with_any(self, header_lexical_forms):
        header = self.is_subordinated_clause()
        it_is = header and header.lexical_form in header_lexical_forms
        return it_is

    def is_subordinated_clause(self):
        if self.is_subordinated() and not self.is_relative():
            header = self.proper_leaves()[0]
            if header.msi["category"] == "conjunction" and header.msi["type"] == "subordinated":
                return header

        return None

    def is_gerund(self):
        return self.verb.msi["mode"] == "gerundio"

    def is_or_inherits_from(self, label):
        if debug_mode: print "--> Clause.is_or_inherits_from(label: ", label, ")"
        node = self.node
        while node:
            if node.label == label:
                return True
            node = node.father
        return False

    def has_structure(self, name):
        return name in [structure.name for structure in self.syntactic_structures]

    def sorted(self, entities, tacit_first):
        return sorted(entities, key=lambda entity: self.index_of(entity, tacit_first))

    def is_assigned(self, entity):
        if debug_mode: print "--> is_assigned(entity) - ", entity
        assigned_entities = self.assigned_entities()
        assigned_directly = entity in assigned_entities
        contained_vector = [assigned.contains(entity) for assigned in assigned_entities]
        assigned_indirectly = any(contained_vector)
        return assigned_directly or assigned_indirectly

    def same_hemiclause(self, node1, node2):
        orig_verb_node = self.original_by_proper(self.verb.node)
        return orig_verb_node.position_of_leaf(node1) == orig_verb_node.position_of_leaf(node2)

    #
    # Methods for accessing ENTITIES
    #
    def subord_entities_closest_to_verb_at(self, side, allowed_distance, which_node=lambda node: True):
        if debug_mode: print "--> Clause.subord_entities_closest_to_verb_at() - side ", side, " - distance ", allowed_distance
        which = lambda entity, node: entity.is_subordinated() \
                                     and entity.highest_subordinating_node() == node \
                                     and which_node(node)
        entities_with_node = self.to_entities_with_node(self.nodes_closest_to_verb_at(side, allowed_distance), which)
        return self.grouped_by_node(entities_with_node)

    def subord_entities(self, which_node=lambda node: True):
        which = lambda entity, node: entity.is_subordinated() and entity.highest_subordinating_node() == node \
                                     and which_node(node)
        entities_with_node = self.to_entities_with_node(list(self.proper_tree()), which)
        return self.grouped_by_node(entities_with_node)

    def verb_level_entities(self):
        by_component = zip(*self.to_entities_with_node(self.verb_level_nodes(), entities=self.entities))
        return list(by_component[0]) if by_component else []

    def entities_closest_to_verb(self, *sides_and_distances):
        entities = []
        for side, distance in sides_and_distances:
            entities.extend(self.entities_closest_to_verb_at(side, distance))
        return entities

    def entities_closest_to_verb_at(self, side, allowed_distance=float("inf")):
        if debug_mode: print "--> Clause.entities_closest_to_verb_at(side, dist) - side: ", side, " - dist: ", allowed_distance
        closest_to_verb = self.nodes_closest_to_verb_at(side, allowed_distance)
        entities_with_node = self.to_entities_with_node(closest_to_verb)
        by_component = zip(*entities_with_node)
        entities = list(by_component[0]) if by_component else []
        return entities

    def entity_by_original(self, node):
        proper_node = self.proper_by_original[node]
        entities = filter(lambda entity: entity.node == proper_node, self.entities)
        return entities[0] if entities else None

    def lonely_entities(self):
        if debug_mode: print "--> Clause.lonely_entities()"
        lonely = [entity for entity in self.entities if not self.is_assigned(entity)]
        return lonely

    def all_entities(self):
        entities = self.entities + self.tacit_entities()
        if self.relative_entity:
            entities.append(self.relative_entity)
        return entities

    def tacit_entities(self):
        return sum([structure.tacit_entities for structure in self.syntactic_structures], [])

    def assigned_entities(self):
        structure_entities = sum([structure.entities for structure in self.syntactic_structures], [])
        return structure_entities

    def assigned_entities_with_referenced_ones(self):
        return [entity.referenced() if entity.is_linked() else entity for entity in self.assigned_entities() +
                self.tacit_entities()]

    #
    # Methods for accessing NODES
    #
    def grouped_by_node(self, entities_with_node):
        entities = []
        last_node = None
        for entity, node in entities_with_node:
            if last_node == node:
                entities[-1].append(entity)
            else:
                entities.append([entity])
            last_node = node
        return entities

    def to_entities_with_node(self, nodes, which=lambda entity, node: entity.node == node, entities=None):
        if debug_mode: print "--> Clause.to_entities_with_node()"
        if not entities:
            entities = self.lonely_entities()

        entities_with_node = []
        for node in nodes:
            entities_with_node.extend((entity, node) for entity in entities if which(entity, node))

        return entities_with_node

    def verb_level_nodes(self):
        verb_node = self.verb.node
        return verb_node.father.children

    def nodes_closest_to_verb_at(self, side, allowed_distance=float("inf")):
        if debug_mode: print "--> Clause.nodes_closest_to_verb_at()"
        verb = self.verb.node
        nodes_with_position = [(verb.absolute_distance_to(node), node) for node in self.verb_level_nodes()
                               if verb.position_of(node) == side]
        closest_with_pos = self.sorted_by_closest(nodes_with_position, allowed_distance)
        closest = [node for position, node in closest_with_pos]
        return closest

    def sorted_by_closest(self, things_with_position, allowed_distance):
        within_distance = filter(lambda (position, entity): position <= allowed_distance,
                                 things_with_position)
        return sorted(within_distance)

    def set_father(self, clause):
        self.father = clause

    def add_child(self, clause):
        self.children.append(clause)

    def proper_leaves(self):
        return self.proper_tree().leaves()

    def put_apart_time_entities(self):
        # Entities created from nodes referencing time most probably are not proper entities.
        # So we add them to clause.time_entities, and remove them from clause.entities to avoid its use in SVO slots

        time_references_with_sub_nodes = []
        for time_reference in self.time_references:
            time_references_with_sub_nodes.append(time_reference)
            for node in time_reference:
                time_references_with_sub_nodes.append(node)

        time_entities_with_references = self.to_entities_with_node(time_references_with_sub_nodes)

        time_references = self.time_references[:]
        time_entities = []
        for (time_entity, time_reference) in time_entities_with_references:
            has_time_word = DateTimeFinder.has_time_word(time_reference)
            kernel_in_time_words = time_entity.kernel and time_entity.kernel.lemma in DateTimeFinder.time_words
            if not has_time_word or kernel_in_time_words:
                time_entities.append(time_entity)
            else:
                if time_reference in time_references:
                    time_references.remove(time_reference)
                    # TODO: also remove sub-nodes from this time_reference

        time_entities = filter(lambda p_entity: p_entity.is_maximal_regarding(time_entities),
                               time_entities)

        self.time_entities = time_entities
        self.time_references = [time_references[0]] if time_references else []

        for time_entity in self.time_entities:
            if time_entity in self.entities:
                self.entities.remove(time_entity)

    def get_hemiclauses(self):
        if debug_mode: print "--> Clause.get_hemiclauses()"
        left_hemiclause_nodes = []
        right_hemiclause_nodes = []

        for orig_node in self.node:
            if type(orig_node) == LeafNode:
                orig_verb_node = self.original_by_proper(self.verb.node)
                if orig_verb_node.position_of_leaf(orig_node) == "left":
                    left_hemiclause_nodes.append(orig_node)

                elif orig_verb_node.position_of_leaf(orig_node) == "right":
                    right_hemiclause_nodes.append(orig_node)

        if debug_mode: print "<-- Clause.get_hemiclauses()"
        return left_hemiclause_nodes, right_hemiclause_nodes

    def relative_linker_words(self):
        return [leaf.lexical_form for leaf in self.relative_linker]

    def original_by_proper(self, proper):
        original_by_proper = {v: k for k, v in self.proper_by_original.items()}
        return original_by_proper[proper]

    def proper_tree(self):
        return self.proper_by_original[self.node]

    def get_number_from_relative_linker(self):
        """

        :rtype : basestring or None
        """
        if not self.is_relative():
            raise Exception("La cláusula no es una relativa (", str(self), ").")

        # ["los cuales", "las cuales", "quienes"],
        is_plural_vector = map(lambda leaf: leaf.msi["number"] is Number.plural, self.relative_linker)

        # ["el cual", "la cual", "quien"]
        is_singular_vector = map(lambda leaf: leaf.msi["number"] is Number.singular, self.relative_linker)

        is_invariable_vector = map(lambda leaf: leaf.msi["number"] is Number.invariable, self.relative_linker)

        if any(is_singular_vector):
            number = Number.singular
        elif any(is_plural_vector):
            number = Number.plural
        elif any(is_invariable_vector):
            number = Number.invariable
        else:
            number = None

        return number

    def get_gender_from_relative_linker(self):
        if debug_mode: print "--> clause.get_gender_from_relative_linker()"

        if not self.is_relative():
            raise Exception("La cláusula no es una relativa (", str(self), ").")

        # "el cual", "los cuales"
        is_masculine_vector = map(lambda leaf: leaf.msi["gender"] is Gender.masculine, self.relative_linker)

        # "la cual", "las cuales"
        is_feminine_vector = map(lambda leaf: leaf.msi["gender"] is Gender.feminine, self.relative_linker)

        is_neutral_vector = map(lambda leaf: leaf.msi["gender"] is Gender.neutral, self.relative_linker)

        if any(is_masculine_vector):
            gender = Gender.masculine
        elif any(is_feminine_vector):
            gender = Gender.feminine
        elif any(is_neutral_vector):
            gender = Gender.neutral
        else:
            gender = None

        return gender

    def structure(self, name):
        return filter(lambda structure: structure.name == name,
                      self.syntactic_structures)[0]

    def leaves_at_left(self):
        root_leaves = self.root().node.leaves()
        first_leaf = self.proper_leaves()[0]
        return root_leaves[:self.index_in_root_of(first_leaf)]

    def index_in_root_of(self, node):
        return self.root().node.leaves().index(self.original_by_proper(node.leaves()[0]))

    def index_of(self, entity, tacit_first):
        tacit_value = float("-inf") if tacit_first else float("inf")
        return tacit_value if entity.is_tacit() else self.proper_leaves().index(entity.leaves()[0])

    #
    # Textual representation
    #
    def __repr__(self):
        return " ".join([str(leaf) for leaf in self.proper_leaves()])
