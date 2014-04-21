#-*- coding: utf-8 -*-

import unittest

from src.parser.labelNode import LabelNode
from src.parser.leafNode import LeafNode


class ParseNodeTest(unittest.TestCase):

    def test_without(self):
        father = LabelNode("father")
        son = LabelNode("son")
        grandson = LeafNode("grandson", "", {})
        other_son = LabelNode("other")

        grandson.set_father(son)
        son.set_father(father)
        other_son.set_father(father)

        pruned = father.cloned_by_original(son)
        cloned = pruned[father]

        self.assertFalse(father.is_equivalent_to(cloned))

        node_id = lambda node: id(node)
        node_intersection = set(map(node_id, father)) & set(map(node_id, cloned))

        self.assertSetEqual(set(), node_intersection)

if __name__ == '__main__':
    unittest.main()