# -*- coding: utf-8 -*-

from clause import *
from parser.inDepthNodeIterator import *
from parser.parseNode import *


class ClauseExtractor:

    def extract_from(self, sentence):
        root = sentence.parse_node
        potential_clause_roots = set(root.nodes_with_labels(self.CLAUSE_SEPARATORS))
        clause_roots = self.filter_invalid_active_voice_clauses(potential_clause_roots)

        if not clause_roots:
            clause_roots = [root]

        roots_by_level = ParseNode.by_level(clause_roots)

        level_parents = set()
        clauses_by_node = {}
        for level, nodes in sorted(roots_by_level.items()):
            for node in nodes:
                clause = Clause(node)
                clauses_by_node[node] = clause
                parents = filter(lambda node: node in level_parents, node.path_to_root())
                if parents:
                    parent = parents[0]
                    father_clause = clauses_by_node[parent]
                    clause.set_father(father_clause)
                    father_clause.add_child(clause)
            level_parents = set(nodes)

        clauses = clauses_by_node.values()
        self.compute_proper_tree_for(clauses)
        return clauses

    def compute_proper_tree_for(self, clauses):
        for clause in clauses:
            original = clause.node
            foreign_nodes = [ child.node for child in clause.children ]
            clause.proper_tree = original.without(foreign_nodes)

    def filter_invalid_active_voice_clauses(self, nodes):
        return filter(lambda node : not node.is_subordinate(), nodes)

    CLAUSE_SEPARATORS = ["grup-verb", "subord-rel", "subord", "subord-ger", "verb-pass"]
