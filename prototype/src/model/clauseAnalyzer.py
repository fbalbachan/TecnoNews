#-*- coding: utf-8 -*-

from src.ling.verb_info import *
from src.model.activeVoiceSyntacticAnalizer import ActiveVoiceSyntacticAnalyzer
from src.model.entity import Entity
from src.model.entityMSISeer import EntityMSISeer
from src.model.passiveVoiceSyntacticAnalyzer import PassiveVoiceSyntacticAnalyzer
from src.model.syntacticAnalyzer import SyntacticAnalyzer
from src.model.syntacticStructure import *
from src.model.verb import Verb


class ClauseAnalyzer:

    def analyze(self, clause):
        print "analyze() clause", clause

        clause.voice = self.voice_of(clause)
        print "\tVoice", clause.voice

        clause.entities = self.entities_of(clause)
        print
        for entity in clause.entities:
            print "\tEntity", entity, entity.msi
        #print "\tMax. entities", map(lambda e: e.leaves(), clause.maximal_entities())

        if clause.voice: clause.verb = self.verb_of(clause)

        print "\n\tSyntactic structures"
        self.analyze_syntactically(clause)
        for structure in clause.syntactic_structures:
            print "\t\t" + structure.name, str(structure)


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
        leaf = self.verb_leaf_of(clause)
        return Verb(leaf, clause.voice)

    def verb_leaf_of(self, clause):
        root = clause.proper_tree
        verb_node = root.nodes_with_labels([ "subord-ger", "verb", "parti-flex" ])
        if len(verb_node) != 1: raise Exception("Existe cero o más de un verbo en la cláusula.")

        return verb_node.pop()

    def entities_of(self, clause):
        root = clause.proper_tree
        entity_labels = ["sn", "patons", "ptonic", "coor-n", "grup-verb-inf"]
        entity_nodes = root.nodes_with_labels(entity_labels)
        entities = [ Entity(node) for node in entity_nodes ]

        entity_msi_seer = EntityMSISeer()
        for entity in entities: entity.msi = entity_msi_seer.msi_of(entity)
        return entities

    def voice_of(self, clause):
        root = clause.proper_tree
        voice_by_label = { "subord-ger": "active", "grup-verb" : "active", "verb-pass" : "passive" }

        if root.label in voice_by_label: return voice_by_label[root.label]

        if root.subordinates_others():
            verbal_node = set([ child.label for child in root.label_node_chlidren() ]) & set(voice_by_label.keys())
            if len(verbal_node) > 1: raise Exception("Se encontró más de un verbo subordinado")
            return voice_by_label[verbal_node.pop()]

        return None