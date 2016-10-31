# -*- coding: utf-8 -*-
from src.utils.tree.treeNode import TreeNode

debug_mode = False

class ParseNode(TreeNode):

    def __init__(self):
        if debug_mode: print "--> ParseNode.Init"
        TreeNode.__init__(self)
        self.token = None

    def set_father(self, father):
        self.father = father
        if father and not self in father.children:
            father.add_child(self)

    def leaves_of_msi(self, msi):
        if debug_mode: print "--> ParseNode.leaves_of_msi"
        return filter(lambda leaf: all([attribute in leaf.msi and leaf.msi[attribute] == value
                                       for attribute, value in msi.items()]), self.leaves())

    def leaves_of_category(self, *categories):
        if debug_mode: print "--> ParseNode.leaves_of_category"
        return sum([self.leaves_of_msi({"category": category}) for category in categories], [])

    def leaves_string(self):
        if debug_mode: print "--> ParseNode.leaves_string"
        return " ".join([str(leaf) for leaf in self.leaves()])

    def lexical_form(self):
        if debug_mode: print "--> ParseNode.lexical_form()"
        leaves = self.leaves()
        forms = [str(leaf) for leaf in leaves if leaf.msi["category"] != "punctuation"]
        lf = " ".join(forms)
        return lf

    def original_lexical_form(self):
        if debug_mode: print "--> ParseNode.original_lexical_form()"

        result = ""
        for leaf in self.leaves():
            orig_form = str(leaf.original_lexical_form)

            between = " " if (len(result) > 0 and leaf.msi["category"] != "punctuation") \
                      else ""

            result = result + between + orig_form

        return result.replace("_", " ")

    def nodes_with_labels(self, labels):
        nodes = []
        for node in self:
            if not node.is_leaf() and node.label in labels:
                nodes.append(node)
        return nodes

    def has_child_with_label(self, label):
        if self.is_leaf() or not self.children:
            return False

        for child in self.children:
            if not child.is_leaf() and child.label == label:
                return True

        return False

    def subordinates_others(self):
        return not self.is_leaf() and self.label in ["subord-rel", "subord"]

    def subordinates_others_special(self):
        if not self.is_leaf() and self.label in ["subord-rel"]:
            if self.level() == 0:
                return False

        return self.subordinates_others()

    def is_subordinate(self):
        return any((node.subordinates_others_special() for node in self.path_to_root()))

    def label_node_children(self):
        if debug_mode: print "--> ParseNode.label_node_children()"
        return filter(lambda child: not child.is_leaf(), self.children)

    def label_lemma_lf_matches(self, labels, lemmas, lexical_forms):
        '''Matches a leaf or a label/leaf pair of nodes with the proper label/lemma as described bellow.

        The condition is stated as follows:
                1) node     is a Leaf or
                            is a label node with only one leaf child
                2) labels   is None   --> any label is valid
                            []        --> only leaf nodes could match
                            is a list --> any label IN the list is valid
                3) lemmas   any label IN Lemmas list is valid
        '''

        if self.is_leaf():
            matches = not lemmas or self.lemma_matches(lemmas)
            matches = matches and (not lexical_forms or self.lexical_form_matches(lexical_forms))
            return matches
        else:
            return self.label_lemma_lf_matches(labels, lemmas, lexical_forms)
