#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from est import *
from estructura import *
from utils.utils import *
from utils.tokenize import *
from conf import *

freeling_client = open('freeling_config/client', 'r').read().strip('\n').strip('FREELING_CLIENT=')
freeling_port = open('freeling_config/port', 'r').read().strip('\n').strip('FREELING_PORT=')
comando = u'echo "%s." | ' + freeling_client + ' localhost:' + freeling_port

class Sentence(object):

    def __init__(self, input_sentence):
        self.valid = True

        # freeling bracketed parse -> structures
        self.input_sentence = input_sentence

        freeling_output = [s.decode('utf-8').strip() for s in os.popen((comando % input_sentence).encode('utf-8')).read().split('\n')]
        if not freeling_output: exit()
        self.flatstructs = filter(lambda x: x.label != 'f-term', [Estructura(e) for e in list(estructuras_balanceadas(freeling_output))])

        # all-spanning tree -> struct for the whole sentence
        self.all = max(filter(lambda x: x.start == 0, self.flatstructs), key=lambda x: x.end)

        # assign children
        for struct in self.flatstructs: struct.children = [s for s in self.flatstructs if struct.contains(s)]

        grup_verbs       = self.by_label('grup-verb')
        verb_pass        = self.by_label('verb-pass')

        self.verbs = filter(lambda e: e.label in ['verb', 'parti-flex'], self.flatstructs)

    def __str__(self):
        return ' | '.join(sorted([e.__str__() for e in self.flatstructs]))

    def by_label(self, label):
        return filter(lambda e: e.label == label, self.flatstructs)

    def hallar_entidades(self):
        sns           = self.by_label('sn')
        grup_verb_inf = self.by_label('grup-verb-inf') # sólo es entity si está a nivel 1
        patons        = self.by_label('paton')
        ptonics       = self.by_label('ptonic')
        coor_ns       = self.by_label('coor_n')

        entities = []
        if sns: entities.extend(sns)
        if grup_verb_inf: entities.extend(grup_verb_inf)
        if patons: entities.extend(patons)
        if ptonics: entities.extend(ptonics)
        if coor_ns: entities.extend(coor_ns)

        return entities

    # sentence API:

    # def get_entities()
    # respecto del verbo
    # def get_rightmost_entity()
    # respecto del verbo
    # def get_leftmost_entity()
    # def get_entity_at_level(n)
    # def get_entity_at_distance(n)
    # def get_svo()

