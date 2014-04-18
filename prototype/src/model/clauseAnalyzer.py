#-*- coding: utf-8 -*-


from logging import getLogger

from src.ling.verb_info import *
from src.model.activeVoiceSyntacticAnalizer import ActiveVoiceSyntacticAnalyzer
from src.model.entityExtractor import EntityExtractor
from src.model.passiveVoiceSyntacticAnalyzer import PassiveVoiceSyntacticAnalyzer
from src.model.syntacticAnalyzer import SyntacticAnalyzer
from src.model.verb import Verb


class ClauseAnalyzer:

    def analyze(self, clause):
        clause.voice = self.voice_of(clause)
        if clause.voice: clause.verb = self.verb_of(clause)
        clause.entities = self.entities_of(clause)
        self.analyze_syntactically(clause)
        self.logger.debug("Result of analyze() clause '%s' voice %s", clause, clause.voice)

    def analyze_syntactically(self, clause):
        syntactic_analyzer_by_voice = { "active" : ActiveVoiceSyntacticAnalyzer,
                                       "passive" : PassiveVoiceSyntacticAnalyzer,
                                       None : SyntacticAnalyzer }
        analyzer = syntactic_analyzer_by_voice[clause.voice](clause)
        analyzer.analyze(self.allowed_syntactic_structures_for(clause))

    def allowed_syntactic_structures_for(self, clause):
        active_voice_structures  = lambda clause: allowed_boxes(clause.verb.transitivity)
        passive_voice_structures = lambda clause: allowed_boxes_for_passive_verbs
        none_voice_structures = lambda clause: allowed_boxes_for_unimember_sentences
        structures_getter_by_voice = { \
                                 None :  none_voice_structures,
                                 "active" : active_voice_structures,
                                 "passive" : passive_voice_structures }
        return structures_getter_by_voice[clause.voice](clause)

    def verb_of(self, clause):
        node = self.verb_node_of(clause)
        leaves = self.verb_leaves_of(clause, node)
        return Verb(node, clause.voice, leaves)

    # Debido a que en voz passiva freeling no agrupa las hojas verbales
    def verb_leaves_of(self, clause, node):
        def leaves_of_passive_voice(clause, node):
            leaves = []
            root = clause.proper_tree
            auxiliar_node = root.nodes_with_labels("vaux")
            if auxiliar_node: leaves.extend(auxiliar_node[0].leaves())

            ser_node = root.nodes_with_labels(["vser", "parti-ser"])
            if ser_node: leaves.extend(ser_node[0].leaves())

            leaves.extend(node.leaves())
            return leaves

        def leaves_of_active_voice(clause, node):
            root = clause.proper_tree
            leaves = node.leaves_of_category("verb")
            ser_node = filter(lambda child: not child.is_leaf() and child.label == "parti-ser", root.children)
            if ser_node: leaves.extend(ser_node[0].leaves())
            return leaves

        verbal_leaves_by_voice = { "active" : leaves_of_active_voice, "passive" : leaves_of_passive_voice }

        return verbal_leaves_by_voice[clause.voice](clause, node)

    def verb_node_of(self, clause):
        root = clause.proper_tree
        verb_node = root.nodes_with_labels([ "subord-ger", "verb", "parti-flex" ])
        if len(verb_node) != 1: raise Exception("Existe cero o más de un verbo en la cláusula.")

        verb_node = verb_node.pop()
        if verb_node.label == "subord-ger": verb_node = verb_node.leaves()[0]

        return verb_node

    def entities_of(self, clause):
        return EntityExtractor(clause).extract()

    def voice_of(self, clause):
        root = clause.proper_tree
        voice_by_label = { "subord-ger": "active", "grup-verb" : "active", "verb-pass" : "passive" }

        if root.label in voice_by_label: return voice_by_label[root.label]

        if root.subordinates_others():
            verbal_node = set([ child.label for child in root.label_node_chlidren() ]) & set(voice_by_label.keys())
            if len(verbal_node) > 1: raise Exception("Se encontró más de un verbo subordinado")
            return voice_by_label[verbal_node.pop()]

        return None

    logger = getLogger("ClauseAnalyzer")