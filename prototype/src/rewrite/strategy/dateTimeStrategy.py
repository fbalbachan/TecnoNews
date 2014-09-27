#-*- coding: utf-8 -*-
from src.rewrite.rewrite import Rewrite

class DateTimeStrategy:
    def __init__(self, ontology):
        self.ontology = ontology

    def applies_to(self, clause):
        return bool(clause.time_references)

    def rewrite(self, clause):
        grouped = self.grouped_references_for(clause)
        groups_with_position = [ (group, self.position_of(group, clause)) for group in grouped ]

        x = sum([ node.leaves() for node in clause.time_references ], [])
        print [ leaf for leaf in clause.proper_leaves() if leaf not in x ]

        return Rewrite(clause.time_references[0], "- LALA -")

    def position_of(self, group, clause):
        all_leaves = filter(lambda leaf: leaf.msi["category"] != "punctuation", clause.proper_leaves())
        start_index = all_leaves.index(group[0].leaves()[0])
        end_index = all_leaves.index(group[-1].leaves()[-1])

        if start_index == 0: return "start"
        elif end_index == len(all_leaves) - 1: return "end"
        else: return "middle"

    def grouped_references_for(self, clause):
        grouped = []
        group = []

        print clause.time_references
        for reference in clause.time_references:
            if not group or self.are_adjacent(group[-1], reference, clause):
                group.append(reference)
            else:
                grouped.append(group)
                group = [ reference ]

        if group: grouped.append(group)
        return grouped

    def are_adjacent(self, node, other, clause):
        all_leaves = filter(lambda leaf: leaf.msi["category"] != "punctuation", clause.proper_leaves())
        return all_leaves.index(node.leaves()[-1]) == all_leaves.index(other.leaves()[0]) - 1

    type = "replacement"
