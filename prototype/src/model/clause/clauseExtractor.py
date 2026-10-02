# -*- coding: utf-8 -*-

from src.model.clause.clause import Clause
from src.parser.parseNode import ParseNode

debug_mode = False


class ClauseExtractor:

    def __init__(self):
        pass

    @staticmethod
    def extract_from(sentence):
        if debug_mode: print("--> ClauseExtractor. extract_from(sentence) - sentence: ", sentence.text)

        clause_separators = ["grup-verb", "subord-rel", "subord", "subord-ger", "verb-pass"]
        root = sentence.parse_node
        potential_clause_roots = set(root.nodes_with_labels(clause_separators))
        potential_clause_roots = ClauseExtractor.filter_invalid_subordinated_clauses(potential_clause_roots)
        if root.label not in ["subord-rel"]:
            clause_roots = set(potential_clause_roots + [root])
        else:
            clause_roots = set(potential_clause_roots)

        roots_by_level = ParseNode.by_level(clause_roots)

        clauses_by_node = {}
        for level, nodes in sorted(roots_by_level.items()):  # @UnusedVariable
            for node in nodes:
                clause = Clause(node)
                clauses_by_node[node] = clause
                parents = [clause_node for clause_node in node.path_to_root() if clause_node in clauses_by_node]
                if parents:
                    parent = parents[0]
                    father_clause = clauses_by_node[parent]
                    clause.set_father(father_clause)
                    father_clause.add_child(clause)

        clauses = list(clauses_by_node.values())

        for clause in clauses:
            clause.proper_by_original = ClauseExtractor.compute_proper_tree_for(clause)

        clauses = ClauseExtractor.without_invalid_clauses(clauses)
        ClauseExtractor.sort_children_of(clauses, sentence)
        clauses = ClauseExtractor.sorted(clauses, sentence)
        return clauses

    @staticmethod
    def sort_children_of(clauses, sentence):
        for clause in clauses:
            clause.children = ClauseExtractor.sorted(clause.children, sentence)

    @staticmethod
    def sorted(clauses, sentence):
        leaves = sentence.parse_node.leaves()
        return sorted(clauses, key=lambda clause: leaves.index(clause.original_by_proper(clause.proper_leaves()[0])))

    @staticmethod
    def without_invalid_clauses(clauses):
        is_cc = lambda leaf: leaf.msi["category"] == "conjunction" and leaf.msi["type"] == "coordinated"
        is_punctuation = lambda leaf: leaf.msi["category"] == "punctuation"
        invalids = [p_clause for p_clause in clauses if all([is_cc(leaf) or is_punctuation(leaf)
                                                for leaf in p_clause.proper_tree().leaves()])]
        only_valid_clauses = lambda p_clause: p_clause not in invalids
        clauses = list(filter(only_valid_clauses, clauses))
        for clause in clauses:
            if clause.father in invalids:
                clause.father = None
            clause.children = list(filter(only_valid_clauses, clause.children))
        return clauses

    @staticmethod
    def compute_proper_tree_for(clause):
        original = clause.node
        foreign_nodes = [child.node for child in clause.children]
        proper_by_original = original.cloned_by_original(foreign_nodes)
        return proper_by_original

    @staticmethod
    def filter_invalid_subordinated_clauses(nodes):
        temp_nodes = [node for node in nodes if node.label not in ["subord-rel"] or (node.label in ["subord-rel"] and node.level() != 0)]
        return [node for node in temp_nodes if not node.is_subordinate() or node.label not in ["grup-verb", "verb-pass"]]
