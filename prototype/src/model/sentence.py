#!/usr/bin/python
# -*- coding: utf-8 -*-
from structure import *
from utils.logger_utils import *
from utils.freeling_utils import FreelingAnalyzer
from ling.msi_mapper import *
from ling.verb_categories import *

class Sentence(object):

    def __init__(self, input_sentence, analyzer=None):
        self.logger = get_logger('entinews')

        self.input_sentence = input_sentence

        if analyzer:
            self.analyzer = analyzer
        else:
            self.analyzer = FreelingAnalyzer()

        # freeling bracketed parse -> structures
        self.freeling_output, self.pretty_freeling_output = self.analyzer.parse(self.input_sentence)
        if not self.freeling_output: return
        self.flatstructs = filter(lambda x: x.label != 'f-term', [Structure(e) for e in list(estructuras_balanceadas(self.freeling_output))])

        # assign children
        for struct in self.flatstructs:
            struct.children = [s for s in self.flatstructs if struct.contains(s)]

        # is_leaf?
        for struct in self.flatstructs: struct.set_leaf_status()

        # assign MSI to all leaves
        self.leaves = [s for s in self.flatstructs if s.is_leaf]
        for leaf in self.leaves:
            leaf.full_msi = tag2fullmsi(leaf.words[0].tag)
            leaf.msi      = msi(leaf.full_msi)

        self.entities = self.get_entities()
        self.equative_entities  = self.get_equative_entities()

        self.grup_verbs = self.by_label('grup-verb')

        # set verb and its lemma & MSI
        try:
            self.verb = self.by_label('verb')[0]
            self.verb.assign_verb_msi()
            self.verb.assign_verb_lemma()
        except IndexError:
            self.verb = None

        # set verb_pass and its lemma & MSI
        try:
            self.verb_pass = self.by_label('verb-pass')[0]
            self.verb_pass.assign_verb_pass_msi()
            self.verb_pass.assign_verb_lemma()
        except IndexError:
            self.verb_pass = None

        # set [active|passive] voice
        self.is_active = self.verb and not(self.verb.is_impersonal_verb()) and not(self.verb_pass) and any([gv.level == 0 for gv in self.grup_verbs]) 
        self.is_passive = self.verb_pass != None
        self.is_unimember = not(self.is_active) and not(self.is_passive)

    def __str__(self):
        return ' | '.join(sorted([e.__str__() for e in self.flatstructs]))

    def by_label(self, label):
        return filter(lambda e: e.label == label, self.flatstructs)

    def get_entities(self):
        sns            = self.by_label('sn')
        grup_verb_infs = self.by_label('grup-verb-inf') # sólo es entity si está a nivel 1
        patons         = self.by_label('patons')
        ptonics        = self.by_label('ptonic')
        coor_ns        = self.by_label('coor-n')

        entities = []
        for group in [sns, patons, ptonics, coor_ns]:
            if group: entities.extend(group)
        if grup_verb_infs: entities.extend(filter(lambda g: g.level == 1, grup_verb_infs))
            
        for entity in entities: entity.assign_noun_msi()

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
