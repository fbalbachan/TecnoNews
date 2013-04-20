#!/usr/bin/python
# -*- coding: utf-8 -*-
from structure import *
from utils.logger_utils import *
from utils.freeling_utils import FreelingAnalyzer
from ling.msi_mapper import *
from ling.verb_categories import *
from ling.tacit_subjects import *

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

        self.grup_verbs = self.by_label('grup-verb')

        # set main verb & sentence voice
        self.verb, self.is_active, self.is_passive = self.get_voice()
        self.is_unimember = not(self.is_active) and not(self.is_passive)

        # find entities
        self.entities = self.get_entities()
        self.equative_entities  = self.get_equative_entities()
        self.entities_at_verb_level = self.assign_entity_position_relative_to_verb()

        # set subject
        self.subject = self.get_subject()

    def __str__(self):
        return ' | '.join(sorted([e.__str__() for e in self.flatstructs]))

    def by_label(self, label):
        return filter(lambda e: e.label == label, self.flatstructs)

    def get_entities(self):
        sns            = self.by_label('sn')
        grup_verb_infs = self.by_label('grup-verb-inf')
        patons         = self.by_label('patons')
        ptonics        = self.by_label('ptonic')
        coor_ns        = self.by_label('coor-n')

        entities = []
        for group in [sns, patons, ptonics, coor_ns]:
            if group: entities.extend(group)
        if grup_verb_infs: entities.extend(filter(lambda g: g.level == 1, grup_verb_infs)) # sólo es entity si está a nivel 1

        for entity in entities: entity.assign_noun_msi()

        return sorted(entities, key=lambda e: e.words[0].position)

    def get_equative_entities(self):
        s_adjs       = self.by_label('s-adj')
        return sorted(s_adjs, key=lambda e: e.words[0].position)

    def get_entity_at_level(self, n):
        return filter(lambda e: e.level == n, self.entities)

    def get_entities_at_distance(self, distance):
        return filter(lambda e: (e.words.pos - self.verb.position) < distance, self.entities)

    # def get_rightmost_entity(), def get_leftmost_entity() # respecto del verbo

    def get_voice(self):
        # set verb and its lemma & MSI
        try:
            active_verb = self.by_label('verb')[0]
            active_verb.assign_verb_lemma()
            active_verb.assign_verb_msi()
        except IndexError:
            active_verb = None

        # set verb_pass and its lemma & MSI
        try:
            passive_verb = self.by_label('verb-pass')[0]
            passive_verb.assign_verb_pass_lemma()
            passive_verb.assign_verb_pass_msi()
        except IndexError:
            passive_verb = None

        is_active = active_verb and not(active_verb.is_impersonal_verb()) and not(passive_verb) and any([gv.level==0 for gv in self.grup_verbs])
        is_passive = passive_verb != None

        if is_active:
            verb = active_verb
        elif is_passive:
            verb = passive_verb
        else:
            verb = active_verb

        return verb, is_active, is_passive

    def assign_entity_position_relative_to_verb(self):
        entities_at_verb_level = filter(lambda entity: entity.level == self.verb.level, self.entities)
        if entities_at_verb_level:
            for (position, struct) in enumerate(sorted(entities_at_verb_level + [self.verb], key=lambda struct: struct.words[0].position)):
                struct.position = position
        return filter(lambda e: e != self.verb, entities_at_verb_level)

    def get_subject(self):
        candidates = self.entities_at_verb_level
        candidates_left_of_verb = [entity for entity in candidates if entity.position < self.verb.position]
        candidates_right_of_verb = [entity for entity in candidates if entity.position > self.verb.position]

        left_candidates = [e for e in candidates_left_of_verb if msi_concordance(e, self.verb)]
        if left_candidates: return left_candidates[0]

        right_candidates = [e for e in candidates_right_of_verb if msi_concordance(e, self.verb) and ((e.position - self.verb.position) < 2)]
        if right_candidates: return right_candidates[0]

        tacit_candidate = tacit_subject_for(self.msi)
        if tacit_candidate: return build_structure(tacit_candidate)