#!/usr/bin/python
# -*- coding: utf-8 -*-
from structure import *
from utils.logger_utils import *
from utils.freeling_utils import FreelingAnalyzer
from ling.msi_mapper import *

class Sentence(object):

    def __init__(self, input_sentence, analyzer=None):
        self.logger = get_logger('entinews')

        self.input_sentence = input_sentence

        if analyzer:
            self.analyzer = analyzer
        else:
            self.analyzer = FreelingAnalyzer()

        # freeling bracketed parse -> structures
        freeling_output = self.analyzer.parse(self.input_sentence)
        if not freeling_output: return
        self.flatstructs = filter(lambda x: x.label != 'f-term', [Structure(e) for e in list(estructuras_balanceadas(freeling_output))])

        # assign children
        for struct in self.flatstructs:
            struct.children = [s for s in self.flatstructs if struct.contains(s)]

        # is_leaf?
        for struct in self.flatstructs:
            struct.set_leaf_status()

        # assign MSI to all leaves
        self.leaves = [s for s in self.flatstructs if s.is_leaf]
        for leaf in self.leaves:
            leaf.full_msi = tag2fullmsi(leaf.words[0].tag)
            # leaf.msi = msi(leaf.full_msi)
            leaf.msi = leaf.get_msi()

        for struct in self.flatstructs:
            struct.assign_msi()
        
        # all-spanning tree -> struct for the whole sentence
        # self.all = None
        # try: self.all = max(filter(lambda x: x.start == 0, self.flatstructs), key=lambda x: x.end)
        # except Exception: logger.info(u"cannot find all-encompassing structure")

        self.verbs = filter(lambda e: e.label in ['verb', 'parti-flex'], self.flatstructs)
        self.main_verb = None
            
        self.entities = self.get_entities()
        self.equative_entities  = self.get_equative_entities()

    def __str__(self):
        return ' | '.join(sorted([e.__str__() for e in self.flatstructs]))

    def by_label(self, label):
        return filter(lambda e: e.label == label, self.flatstructs)

    def get_entities(self):
        sns           = self.by_label('sn')
        grup_verb_inf = self.by_label('grup-verb-inf') # sólo es entity si está a nivel 1
        patons        = self.by_label('paton')
        ptonics       = self.by_label('ptonic')
        coor_ns       = self.by_label('coor-n')

        entities = []

        for group in [sns,grup_verb_inf, patons, ptonics, coor_ns]:
            if group: entities.extend(group)

        return sorted(entities, key=lambda e: e.words[0].position) 

    def get_equative_entities(self):
        s_adjs       = self.by_label('s-adj')

        return sorted(s_adjs, key=lambda e: e.words[0].position) 

    def get_entity_at_level(self, n):
        return filter(lambda e: e.level == n, self.entities)

    # def get_entities_at_distance(self, distance, verb_position=None):
    #     if verb_position == None: verb_position = self.main_verb.words[0].position
    #     return filter(lambda e: (e.words.pos - verb_position) < distance)

    # sentence API:

    # def get_rightmost_entity(), def get_leftmost_entity() # respecto del verbo

    # def get_svo()
