#-*- coding: utf-8 -*-
from src.model.entity.verb import Verb


class VerbExtractor:
    def __init__(self, clause):
        self.clause = clause

    def extract(self):
        node = self.verb_node()
        leaves = self.verb_leaves_of(node)
        return Verb(node, self.clause.voice, leaves)

    # Debido a que en voz passiva freeling no agrupa las hojas verbales
    def verb_leaves_of(self, node):
        def leaves_of_passive_voice(clause, node):
            leaves = []
            root = clause.proper_tree()
            auxiliar_node = root.nodes_with_labels("vaux")
            if auxiliar_node: leaves.extend(auxiliar_node[0].leaves())

            ser_node = root.nodes_with_labels(["vser", "parti-ser"])
            if ser_node: leaves.extend(ser_node[0].leaves())

            leaves.extend(node.leaves())
            return leaves

        def leaves_of_active_voice(clause, node):
            root = clause.proper_tree()
            leaves = node.leaves_of_category("verb")

            if leaves[0].lemma == "estar":
                if not (len(leaves) > 1 and leaves[1].msi["mode"] == "gerundio"): leaves = [ leaves[0] ]
                return leaves

            ser_node = filter(lambda child: not child.is_leaf() and child.label == "parti-ser", root.children)
            if ser_node: leaves.extend(ser_node[0].leaves())
            return leaves

        verbal_leaves_by_voice = { "active" : leaves_of_active_voice, "passive" : leaves_of_passive_voice }

        clause = self.clause
        return verbal_leaves_by_voice[clause.voice](clause, node)

    def verb_node(self):
        root = self.clause.proper_tree()
        verb_nodes = root.nodes_with_labels([ "subord-ger", "verb", "parti-flex" ])
        verb_nodes = sorted(verb_nodes, key = lambda node: node.level())

        node = verb_nodes[0]
        if node.label == "subord-ger": node = node.leaves()[0]
        return node
