# -*- coding: utf-8 -*-

from re import search

from src.ling.msi_mapper import *
from src.parser.labelNode import *
from src.parser.leafNode import *
from src.utils.spacyClientParser import SpacyClientParser


class FreelingTreeParser:

    def from_text(self, text):
        output = SpacyClientParser().parse(text)
        return self.parse(output)

    def from_file(self, path):
        file = open(path, encoding="utf-8")
        output = file.read().split("\n")
        return self.parse(output)

    def parse(self, output):
        node_stack = []
        father = None

        for line in output:
            if not line:
                continue

            if node_stack:
                father = node_stack[-1]

            if not self.is_level_ending(line):
                node = self.node_for(line)
                if father:
                    father.add_child(node)
                if not self.is_leaf(line):
                    node_stack.append(node)
            else:
                node_stack.pop()

        return father

    def node_for(self, line):
            if self.is_leaf(line):
                return self.leaf_node_for(line)
            else:
                return self.label_node_for(line)

    def label_node_for(self, line):
        label = self.middle_node_label_of(line)
        return LabelNode(label)

    def leaf_node_for(self, line):
        regex_match = self.leaf_node_match_for(line)
        lexical_form = regex_match.group(1)
        lemma = regex_match.group(2)
        leaf_msi = tag_to_full_msi(regex_match.group(3))
        return LeafNode(lexical_form, lemma, leaf_msi)

    def middle_node_label_of(self, line):
        return search("\+?([-a-zA-Z]+)_\[", line.strip()).group(1)

    def is_level_ending(self, line):
        return line.strip() == "]"

    def is_leaf(self, line):
        return self.leaf_node_match_for(line) is not None

    def leaf_node_match_for(self, line):
        return search("^\+?\(([^ ]+) ([^ ]+) (\w+) -\)$", line.strip())

    def level_of(self, line):
        line_indentation = search("^ *", line).group(0)
        return len(line_indentation) // self.SPACES_PER_LEVEL

    SPACES_PER_LEVEL = 2