# -*- coding: utf-8 -*-
from src.model.entity.verb import Verb

debug_mode = False


class VerbExtractor:
    def __init__(self, clause):
        self.clause = clause

    def extract(self):
        if debug_mode: print "--> VerbExtractor.extract()"
        node = self._verb_node()
        leaves = self._verb_leaves_of(node)
        verb = Verb(node, self.clause.voice, leaves)
        return verb

    # Freeling does not group verb leaves for the passive voice. This method does that.
    def _verb_leaves_of(self, node):
        if debug_mode: print "--> VerbExtractor._verb_leaves_of()"

        def _leaves_of_passive_voice(p_clause, p_node):
            leaves = []
            root = p_clause.proper_tree()
            auxiliary_node = root.nodes_with_labels("vaux")
            if auxiliary_node:
                leaves.extend(auxiliary_node[0].leaves())

            ser_node = root.nodes_with_labels(["vser", "parti-ser"])
            if ser_node:
                leaves.extend(ser_node[0].leaves())

            leaves.extend(p_node.leaves())
            return leaves

        def _leaves_of_active_voice(p_clause, p_node):
            if debug_mode: print "--> VerbExtractor._leaves_of_active_voice()"

            root = p_clause.proper_tree()
            leaves = p_node.leaves_of_category("verb")

            if leaves[0].lemma == "estar":
                if not (len(leaves) > 1 and leaves[1].msi["mode"] == "gerundio"):
                    leaves = [leaves[0]]
                return leaves

            ser_node = filter(lambda child:
                                    not child.is_leaf() and child.label == "parti-ser",
                              root.children)
            if ser_node:
                leaves.extend(ser_node[0].leaves())

            return leaves

        verbal_leaves_by_voice = {"active": _leaves_of_active_voice,
                                  "passive": _leaves_of_passive_voice}
        clause = self.clause
        return verbal_leaves_by_voice[clause.voice](clause, node)

    def _verb_node(self):
        if debug_mode: print "--> VerbExtractor._verb_node()"
        root = self.clause.proper_tree()
        verb_nodes = root.nodes_with_labels(["subord-ger", "verb", "parti-flex"])
        verb_nodes = sorted(verb_nodes, key=lambda p_node: p_node.level())

        node = verb_nodes[0]
        if node.label == "subord-ger":
            leaves = node.leaves()
            node = leaves[0]

        return node
