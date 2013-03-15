#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from est import *
from estructura import *
from utils.utils import *
from utils.tokenize import *
# from utils.ling import *
from svo import *
from clausula import *
from conf import *

freeling_client = open('freeling_config/client', 'r').read().strip('\n').strip('FREELING_CLIENT=')
freeling_port = open('freeling_config/port', 'r').read().strip('\n').strip('FREELING_PORT=')

def marca_de_negacion(w):
    return w.lemma in marcas_negacion

class Oracion(object):
    """Oracion(Clausula(SVO), Clausula(SVO), Clausula(SVO))"""
    def __init__(self, sentence):
        self.id = 0
        self.valid = True
        self.hay_negacion = False

        # freeling bracketed parse -> structures
        self.input_text = sentence
        self.detrolled_text = detroll(sentence)
        comando = u'echo "%s." | ' + freeling_client + ' localhost ' + freeling_port
        freeling_output = [s.decode('utf-8').strip() for s in os.popen((comando % sentence).encode('utf-8')).read().split('\n')]
        if not freeling_output: exit()
        self.flatstructs = filter(lambda x: x.label != 'f-term', [Estructura(e) for e in list(estructuras_balanceadas(freeling_output))])

        # all-spanning tree -> struct for the whole sentence
        self.all = max(filter(lambda x: x.start == 0, self.flatstructs), key=lambda x: x.end)

        # avoid negation and passive-voice (for now)
        # if self.by_label(marca_pasiva) != []:
        #     self.valid = False
        #     return

        # if anything is negated, turn off verbal sentiment assignment
        if any([marca_de_negacion(w) for w in self.all.words]): self.hay_negacion = True

        # assign children
        for struct in self.flatstructs: struct.children = [s for s in self.flatstructs if struct.contains(s)]

        # sentence is coordination
        in_coord_vb         = len(self.by_label('coor-vb')) > 0

        # sentence has clauses
        grup_verbs       = self.by_label('grup-verb')
        verb_pass        = self.by_label('verb-pass')
        subords          = self.by_label('subord')
        subord_rels      = self.by_label('subord-rel')
        valid_grup_verbs = [g for g in grup_verbs if (not(g.is_contained_by_any(subords)) and not(g.is_contained_by_any(subord_rels)))]
        groups = []
        if valid_grup_verbs: groups.extend(valid_grup_verbs)
        if subord_rels: groups.extend(subord_rels)
        if subords: groups.extend(subords)
        if verb_pass: groups.extend(verb_pass)

        self.clauses = []

        verbs = filter(lambda e: e.label in ['verb', 'parti-flex'], self.flatstructs)
        if not verbs:
            # whole sentence is one clause - that whole clause is a subject
            main_clause = Clausula(self.all)
            main_clause.is_whole_sentence = True
            main_clause.svo = SVO()

            main_clause.hallar_entidades()
            if main_clause.entidades_sujeto:
                main_clause.svo.subject = SVOelement(main_clause.entidades_sujeto[0])

            rgs = filter(lambda w: w.tag == 'RG', self.all.words)
            sadvs = []
            main_clause.svo.adverbs = []
            for rg in rgs:
                rg_sadv = get_estructura_vacia()
                rg_sadv.label = rg.tag
                rg_sadv.start = rg.position
                rg_sadv.end = rg.position
                rg_sadv.words = [rg]
                main_clause.svo.adverbs.append(SVOelement(rg_sadv))

            main_clause.svo.build()
            self.clauses = [main_clause]
        else:
            # sentence is made of clauses
            self.clauses.extend([Clausula(g.quitar(subords).quitar(subord_rels), in_coord_vb) for g in groups])

    def __repr__(self):
        return ' | '.join(sorted([e.__repr__() for e in self.flatstructs])).encode('utf-8')

    def __str__(self):
        return ' | '.join([clause.__str__() for clause in self.clauses])
        
    def by_label(self, label):
        return filter(lambda e: e.label == label, self.flatstructs)
