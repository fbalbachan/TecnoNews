#!/usr/bin/env python
#-*- coding: utf-8 -*-

from labelNode import *
from leafNode import *
from re import search


class FreelingTreeParser:
    def from_file(self, path):
        file = open(path)
        output = file.read().split("\n")
        return self.parse(output)

    def from_text(self, text):
        freeling_client = FreelingClientParser()
        output= freeling_client.parse(text)
        return self.parse(output)

    def parse(self, output):
        node_stack = []
        father = None

        for line in output:
            if not line: continue
            if node_stack:
                father = node_stack[-1]

            if not self.is_level_ending(line):
                node = self.node_for(line)
                if father:
                    node.set_father(father)
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
        lexicalForm = regex_match.group(1)
        lemma = regex_match.group(2)
        msi = regex_match.group(3)
        return LeafNode(lexicalForm, lemma, msi)

    def middle_node_label_of(self, line):
        return search("\+?([-a-zA-Z]+)_\[", line.strip()).group(1)

    def is_level_ending(self, line):
        return line.strip() == "]"

    def is_leaf(self, line):
        return self.leaf_node_match_for(line) is not None

    def leaf_node_match_for(self, line):
        return search(self.LEAF_NODE_REGEX, line.strip())

    def level_of(self, line):
        line_indentation = search("^ *", line).group(0)
        return len(line_indentation) / self.SPACES_PER_LEVEL

    SPACES_PER_LEVEL = 2
    LEAF_NODE_REGEX = "^\+\(([^ ]+) ([^ ]+) (\w+) -\)$"

tree_parser = FreelingTreeParser()
print tree_parser.from_file("parse_tree.txt").tree_representation()
