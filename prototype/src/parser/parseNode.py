#-*- coding: utf-8 -*-
from src.utils.tree.treeNode import TreeNode


class ParseNode(TreeNode):

    def set_father(self, father):
        self.father = father
        if father and not self in father.children:
            father.add_child(self)

    def __init__(self):
        TreeNode.__init__(self)

    def leaves_of_msi(self, msi):
        return filter(lambda leaf: all([ attribute in leaf.msi and leaf.msi[attribute] == value
                                       for attribute, value in msi.items() ]), self.leaves())

    def leaves_of_category(self, *categories):
        return sum([ self.leaves_of_msi({ "category" : category }) for category in categories ], [])

    def leaves_string(self):
        return " ".join([ str(leaf) for leaf in self.leaves() ])

    def nodes_with_labels(self, labels):
        nodes = []
        for node in self:
            if not node.is_leaf() and node.label in labels:
                nodes.append(node)
        return nodes

    def subordinates_others(self):
        return not self.is_leaf() and self.label in ["subord-rel", "subord"]

    def is_subordinate(self):
        return any( (node.subordinates_others() for node in self.path_to_root()) )

    def label_node_chlidren(self):
        return filter(lambda child: not child.is_leaf(), self.children)
