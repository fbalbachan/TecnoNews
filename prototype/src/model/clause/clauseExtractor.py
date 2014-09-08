# -*- coding: utf-8 -*-

from src.model.clause.clause import Clause
from src.parser.parseNode import ParseNode


class ClauseExtractor:

    def extract_from(self, sentence):
        root = sentence.parse_node
        potential_clause_roots = set(root.nodes_with_labels(self.CLAUSE_SEPARATORS))
        clause_roots = set(self.filter_invalid_subordinated_clauses(potential_clause_roots) + [root])
        roots_by_level = ParseNode.by_level(clause_roots)

        clauses_by_node = {}
        for level, nodes in sorted(roots_by_level.items()):  # @UnusedVariable
            for node in nodes:
                clause = Clause(node)
                clauses_by_node[node] = clause
                parents = filter(lambda node: node in clauses_by_node, node.path_to_root())
                if parents:
                    parent = parents[0]
                    father_clause = clauses_by_node[parent]
                    clause.set_father(father_clause)
                    father_clause.add_child(clause)

        clauses = clauses_by_node.values()
        self.compute_proper_tree_for(clauses)
        clauses = self.without_invalid_clauses(clauses)
        self.sort_children_of(clauses, sentence)

        return self.sorted(clauses, sentence)

    def sort_children_of(self, clauses, sentence):
        for clause in clauses:
            clause.children = self.sorted(clause.children, sentence)

    def sorted(self, clauses, sentence):
        leaves = sentence.parse_node.leaves()
        return sorted(clauses, key = lambda clause: leaves.index(clause.original_by_proper(clause.proper_leaves()[0])))

    def without_invalid_clauses(self, clauses):
        is_cc = lambda leaf: leaf.msi["category"] == "conjunction" and leaf.msi["type"] == "coordinated"
        is_punctuation  = lambda leaf: leaf.msi["category"] == "punctuation"
        invalids = filter(lambda clause: all([ is_cc(leaf) or is_punctuation(leaf)
                                              for leaf in clause.proper_tree().leaves() ]), clauses)
        only_valid_clauses = lambda clause: clause not in invalids
        clauses = filter(only_valid_clauses, clauses)
        for clause in clauses:
            if clause.father in invalids: clause.father = None
            clause.children = filter(only_valid_clauses, clause.children)
        return clauses

    def compute_proper_tree_for(self, clauses):
        for clause in clauses:
            original = clause.node
            foreign_nodes = [ child.node for child in clause.children ]
            clause.proper_by_original = original.cloned_by_original(foreign_nodes)

    def filter_invalid_subordinated_clauses(self, nodes):
        return filter(lambda node : not node.is_subordinate()
                      or (node.is_subordinate() and node.label not in ["grup-verb", "verb-pass"]), nodes)

    CLAUSE_SEPARATORS = ["grup-verb", "subord-rel", "subord", "subord-ger", "verb-pass"]
