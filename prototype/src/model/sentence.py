#!/usr/bin/python
# -*- coding: utf-8 -*-
from structure import *
from utils.logger_utils import *
from utils.freeling_utils import FreelingAnalyzer
from ling.msi_mapper import *
from ling.verb_categories import *
from ling.tacit_subjects import *
from ling.verb_info import *

class Sentence(object):

    def __init__(self, input_sentence, analyzer=None):
        # self.logger = get_logger('entinews')

        self.evidence = u''

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
            if leaf.label != u'fc':
                leaf.full_msi = tag2fullmsi(leaf.words[0].tag)
                leaf.msi      = msi(leaf.full_msi)

        self.grup_verbs = self.by_label('grup-verb')

        # FIXME: so far, only grup-verb sentences
        self.all_encompassing_structure = self.grup_verbs[0]

        self.all_words = self.all_encompassing_structure.words

        # set main verb & sentence voice
        self.verb, self.is_active, self.is_passive = self.get_voice_and_verb()
        self.is_unimember = not(self.is_active) and not(self.is_passive)

        # find entities
        self.entities = self.get_entities()
        self.equative_entities  = self.get_equative_entities()
        self.structures_at_verb_level = self.assign_structure_position_relative_to_verb()

        self.subject = None

        self.od       = None
        self.oi       = None
        self.regimen  = None
        self.equative = None
        self.adjuncts = None

        self.boxes   = None

        if self.verb:

            # get verb info
            self.verb_script_class = get_script_class(self.verb.lemma)
            self.verb_transitivity = get_transitivity(self.verb.lemma)

            # set up available boxes
            self.boxes = allowed_boxes(self.verb_transitivity)

            # fill verb box
            self.boxes['verb'] = self.verb.words[-1].lemma

            # set subject
            self.subject = self.get_subject()

            # fill allowed boxes
            if self.boxes['od']: self.od = self.get_od()
            if self.boxes['oi']: self.oi = self.get_oi()
            if self.boxes['regimen']: self.regimen = self.get_regimen()
            if self.boxes['equative']: self.equative = self.get_equative()
            if self.boxes['adjuncts']: self.adjuncts = self.get_adjuncts()


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

        for entity in entities:
            entity.assign_noun_msi()
            entity.assign_entity_type()

        return sorted(entities, key=lambda e: e.words[0].position)

    def get_equative_entities(self):
        s_adjs       = self.by_label('s-adj')
        return sorted(s_adjs, key=lambda e: e.words[0].position)

    def get_entity_at_level(self, n):
        return filter(lambda e: e.level == n, self.entities)

    def get_voice_and_verb(self):
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

        if is_passive:
            verb = passive_verb
        else:
            verb = active_verb

        # verb.assign_verb_position()
        return verb, is_active, is_passive

    def assign_structure_position_relative_to_verb(self):
        try:
            structures_at_verb_level = filter(lambda entity: entity.level == self.verb.level, self.entities + self.by_label('grup-sp') + self.by_label('sp-de') + self.by_label('s-adj'))
        except AttributeError: return [] # no verb | no entities
        if structures_at_verb_level:
            for (position, struct) in enumerate(sorted(structures_at_verb_level + [self.verb], key=lambda x: x.words[0].position)):
                struct.position = position
        return filter(lambda e: e.position != self.verb.position, structures_at_verb_level)

    def get_subject(self):
        candidates = filter(lambda e: e.label != 'grup-sp', self.structures_at_verb_level)
        candidates_left_of_verb = [entity for entity in candidates
                                   if entity.position < self.verb.position and entity.entity_type == 'proper_entity']
        candidates_right_of_verb = [entity for entity in candidates
                                    if entity.position > self.verb.position and entity.entity_type == 'proper_entity']
        if candidates_left_of_verb:
            left_candidates = [e for e in candidates_left_of_verb if e.msi and msi_concordance(e, self.verb)]
            if left_candidates:
                self.evidence += "\nsubject: 1"
                return sorted(left_candidates, key=lambda e: self.verb.position - e.position)[0]
                
        if candidates_right_of_verb:
            right_candidates = [e for e in candidates_right_of_verb if e.msi and msi_concordance(e, self.verb) and ((e.position - self.verb.position) <= 3)]
            if right_candidates:
                self.evidence += "\nsubject: 2"
                return sorted(right_candidates, key=lambda e: e.position - self.verb.position)[0]

        tacit_candidate = tacit_subject_for(self.verb)
        tacit_subject = build_structure(word=tacit_candidate)
        tacit_subject.msi = self.verb.msi
        return tacit_subject

    def get_od(self):

        # 1) proper entities
        proper_entities = filter(lambda e:
                                 e.entity_type and (e.entity_type == 'proper_entity') and
                                 not e.conflicts_with(self.subject),
                                 self.entities)

        if proper_entities:
            proper_entities_right_of_verb = [entity for entity in proper_entities if entity.words[0].position > self.verb.words[0].position]
            if proper_entities_right_of_verb:

                # 1.1) a derecha
                # 1.1.1) a distancia <= 3, al mismo nivel
                candidates = filter(lambda entity:
                                    entity.level == self.verb.level and
                                    not entity.conflicts_with(self.subject) and
                                    abs(entity.position - self.verb.position) <= 3,
                                    proper_entities_right_of_verb)
                if candidates:
                    self.evidence += "\nod: 1.1.1"
                    return sorted(candidates, key=lambda entity: entity.position)[0]

                # 1.1.2) contenida en sp y a distancia <= 3
                sps = self.by_label('grup-sp')
                if sps:
                    for entity in proper_entities_right_of_verb:
                        sps_containing_candidate_entity = filter(lambda sp:
                                                                 sp.level == self.verb.level and
                                                                 sp.contains(entity) and
                                                                 sp.words[0].lemma == u'a' and
                                                                 abs(sp.position - self.verb.position) <= 3 and
                                                                 not entity.conflicts_with(self.subject), sps)
                        if sps_containing_candidate_entity:
                            self.evidence += "\nod: 1.1.2"
                            return entity

                # 1.2) a izquierda
                # 1.2.1) distancia <= 2, al mismo nivel
                proper_entities_left_of_verb = [entity for entity in proper_entities if not(entity in proper_entities_right_of_verb)]
                candidates = filter(lambda entity: entity.level == self.verb.level
                                    and abs(entity.position - self.verb.position) <= 2 and
                                    not entity.conflicts_with(self.subject),
                                    proper_entities_left_of_verb)
                if candidates:
                    self.evidence += "\nod: 1.2.1"
                    return sorted(candidates, key=lambda entity: entity.position)[0]

                # 1.2.2) sp encabezado por 'a' con distancia <= 2
                if sps:
                    for entity in proper_entities_left_of_verb:
                        sps_containing_candidate_entity = filter(lambda sp:
                                                                 sp.level == self.verb.level and
                                                                 sp.contains(entity) and
                                                                 sp.words[0].lemma == u'a' and
                                                                 abs(sp.position - self.verb.position) <= 2 and
                                                                 not entity.conflicts_with(self.subject), sps)
                        if sps_containing_candidate_entity:
                            self.evidence += "\nod: 1.2.2"
                            return entity

        # 2) pronominal entities
        pronominal_entities = filter(lambda e:
                                     e.entity_type and (e.entity_type == 'pronominal_entity') and
                                     not e.conflicts_with(self.subject),
                                     self.entities)
        if pronominal_entities:
            # 2.1) a izquierda
            # 2.1.1) con distancia <= 2
            pronominal_entities_left_of_verb = [entity for entity in pronominal_entities
                                                if entity.words[0].position < self.verb.words[0].position]
            if pronominal_entities_left_of_verb:
                candidates = filter(lambda e:
                                    e.level == self.verb.level and
                                    abs(e.position - self.verb.position) <= 2 and
                                    not e.conflicts_with(self.subject),
                                    pronominal_entities_left_of_verb)
                if candidates:
                    self.evidence += "\nod: 2.1.1"
                    return sorted(candidates, key=lambda e: e.position)[0]

            # 2.2) a derecha
            # 2.2.1) con distancia <= 2
            pronominal_entities_right_of_verb = [entity for entity in pronominal_entities if entity.words[0].position > self.verb.words[0].position]
            if pronominal_entities_right_of_verb:
                candidates = filter(lambda e:
                                    e.level == self.verb.level and
                                    abs(e.position - self.verb.position) <= 2 and
                                    not e.conflicts_with(self.subject),
                                    pronominal_entities_right_of_verb)
                if candidates:
                    self.evidence += "\nod: 2.2.1"
                    return sorted(candidates, key=lambda e: e.position)[0]

        return None

    def get_oi(self):

        if not(self.is_active):
            self.evidence += "\noi: 0.1"
            return None

        if self.verb_transitivity == 'TRANSITIVE' and not(self.od):
            self.evidence += "\noi: 0.2"
            return None

        proper_entities_right_of_verb = filter(lambda e: e.entity_type == 'proper_entity' and
                                               e.words[0].position > self.verb.words[0].position and
                                               not e.conflicts_with(self.subject, self.od),
                                               self.entities)

        proper_entities_left_of_verb = filter(lambda e: e.entity_type == 'proper_entity' and
                                              e.words[0].position < self.verb.words[0].position and
                                              not e.conflicts_with(self.subject, self.od),
                                              self.entities)

        if proper_entities_right_of_verb:
            # 1) a derecha

            # 1.1) sp con distancia <= 3; entidad dentro de sp a nivel (sp+1)
            sps = self.by_label('grup-sp')
            sps_a = filter(lambda sp: sp.level == self.verb.level and
                           sp.words[0].lemma == u'a' and
                           abs(sp.position - self.verb.position) <= 3,
                           sps)
            if sps_a:
                for sp_a in sps_a:
                    for entity in sorted(proper_entities_right_of_verb, key=lambda e: e.position):
                        if (sp_a.contains(entity)) and (entity.level == (sp_a.level + 1)):
                            self.evidence += "\noi: 1.1"
                            return entity

        # 2) a izquierda
        # 2.1) a distancia <= 2, al mismo nivel
        entities_at_verb_level = filter(lambda entity: entity.level == self.verb.level, self.entities)
        pronominal_entities_left_of_verb = [entity for entity in entities_at_verb_level
                                            if (entity.position < self.verb.position) and
                                            (entity.entity_type == 'pronominal_entity') and
                                            not entity.conflicts_with(self.subject, self.od)]
        if pronominal_entities_left_of_verb:
            candidates = filter(lambda e: e.level == self.verb.level and
                                abs(e.position - self.verb.position) <= 2,
                                pronominal_entities_left_of_verb)
            if candidates:
                if self.od: candidates = filter(lambda c: c.words[0].position != self.od.words[0].position, candidates)
                if candidates:
                   self.evidence += "\noi: 2.1"
                   return sorted(candidates, key=lambda e: e.position)[-1]

        # 2.2) sp con distancia <= 3, al mismo nivel; entidad dentro de sp a nivel (sp+1)
        sps = self.by_label('grup-sp')
        sps_a = filter(lambda sp: sp.words[0].lemma == u'a' and
                       sp.level == self.verb.level and
                       abs(sp.position - self.verb.position) <= 3,
                       sps)
        if sps_a:
            for sp_a in sps_a:
                for entity in sorted(proper_entities_left_of_verb, key=lambda e: e.position, reverse=True):
                    if (sp_a.contains(entity)) and (entity.level == (sp_a.level + 1)):
                        self.evidence += "\noi: 2.2"
                        return entity
        
        return None

    def get_regimen(self):

        if not(self.is_active):
            self.evidence += "\nregimen: 0.1"
            return None

        # 1) grup-sp
        sps = self.by_label('grup-sp')

        if sps:
            # 1.1) a derecha, distancia <= 3
            sps_right_of_verb_at_verb_level = filter(lambda sp: (sp.level == self.verb.level)
                                                     and (sp.position > self.verb.position)
                                                     and abs(sp.position - self.verb.position) <= 3,
                                                     sps)
            if sps_right_of_verb_at_verb_level:
                proper_entities_right_of_verb = filter(lambda e: e.entity_type == 'proper_entity' and
                                                       e.words[0].position > self.verb.words[0].position and
                                                       not e.conflicts_with(self.subject, self.od, self.oi),
                                                       self.entities)
                for sp in sps_right_of_verb_at_verb_level:
                    for entity in sorted(proper_entities_right_of_verb, key=lambda e: e.position):
                        if (sp.contains(entity)) and (entity.level == (sp.level + 1)):
                            self.evidence += "\nregimen: 1.1"
                            return entity

            # 1.2) a izquierda, distancia <= 3
            sps_left_of_verb_at_verb_level = filter(lambda sp: (sp.level == self.verb.level)
                                                     and (sp.position < self.verb.position)
                                                     and abs(sp.position - self.verb.position) <= 3,
                                                     sps)
            if sps_left_of_verb_at_verb_level:
                proper_entities_left_of_verb = filter(lambda e: e.entity_type == 'proper_entity' and
                                                       e.words[0].position < self.verb.words[0].position and
                                                       not e.conflicts_with(self.subject, self.od, self.oi),
                                                       self.entities)
                for sp in sps_left_of_verb_at_verb_level:
                    for entity in sorted(proper_entities_left_of_verb, key=lambda e: e.position, reverse=True):
                        if (sp.contains(entity)) and (entity.level == (sp.level + 1)):
                            self.evidence += "\nregimen: 1.2"
                            return entity

        # 2) grup-sp-de
        sps_des = self.by_label('sp-de')

        if sps_des:
            # 2.1) a derecha, distancia <= 3
            sps_des_right_of_verb_at_verb_level = filter(lambda sp: (sp.level == self.verb.level)
                                                         and (sp.position > self.verb.position)
                                                         and abs(sp.position - self.verb.position) <= 3,
                                                         sps_des)

            if sps_des_right_of_verb_at_verb_level:
                proper_entities_right_of_verb = filter(lambda e: e.entity_type == 'proper_entity' and
                                                       e.words[0].position > self.verb.words[0].position and
                                                       not e.conflicts_with(self.subject, self.od, self.oi),
                                                       self.entities)
                for sp in sps_des_right_of_verb_at_verb_level:
                    for entity in sorted(proper_entities_right_of_verb, key=lambda e: e.position, reverse=True):
                        if (sp.contains(entity)) and (entity.level == (sp.level + 1)):
                            self.evidence += "\nregimen: 2.1"
                            return entity

            # 2.2) a izquierda, distancia <= 2
            sps_des_left_of_verb_at_verb_level = filter(lambda sp: (sp.level == self.verb.level)
                                                        and (sp.position < self.verb.position)
                                                        and abs(sp.position - self.verb.position) <= 3,
                                                        sps_des)
            if sps_left_of_verb_at_verb_level:
                proper_entities_left_of_verb = filter(lambda e: e.entity_type == 'proper_entity' and
                                                       e.words[0].position < self.verb.words[0].position and
                                                       not e.conflicts_with(self.subject, self.od, self.oi),
                                                       self.entities)
                for sp in sps_des_left_of_verb_at_verb_level:
                    for entity in sorted(proper_entities_left_of_verb, key=lambda e: e.position, reverse=True):
                        if (sp.contains(entity)) and (entity.level == (sp.level + 1)):
                            self.evidence += "\nregimen: 2.2"
                            return entity

        return None

    def get_equative(self):

        if not(self.is_active):
            self.evidence += "\nequative: 0.1"
            return None

        # 1) s-adj
        s_adjs = self.by_label('s-adj')

        if s_adjs:
            # 1.1) a derecha, distancia <= 3
            s_adjs_right_of_verb_at_verb_level = filter(lambda s_adj:
                                                        (s_adj.level == self.verb.level)
                                                        and (s_adj.position > self.verb.position)
                                                        and abs(s_adj.position - self.verb.position) <= 3
                                                        and not s_adj.conflicts_with(self.subject, self.od, self.oi, self.regimen),
                                                        s_adjs)
            if s_adjs_right_of_verb_at_verb_level:
                self.evidence += "\nequative: 1.1"
                return sorted(s_adjs_right_of_verb_at_verb_level, key=lambda s: s.position)[0]

            # 1.2) a izquierda, distancia <= 3
            s_adjs_left_of_verb_at_verb_level = filter(lambda s:
                                                       (s_adj.level == self.verb.level)
                                                       and (s_adj.position < self.verb.position)
                                                       and abs(s_adj.position - self.verb.position) <= 2
                                                       and not s_adj.conflicts_with(self.subject, self.od, self.oi, self.regimen),
                                                       s_adjs)
            if s_adjs_left_of_verb_at_verb_level:
                self.evidence += "\nequative: 1.2"
                return sorted(sps_des_left_of_verb_at_verb_level, key=lambda s: s.position)[-1]

        # 2) entidades propiamente dichas, a derecha, distancia <= 3
        candidates = filter(lambda e: (e.level == self.verb.level)
                            and (e.position > self.verb.position)
                            and e.entity_type == 'proper_entity' 
                            and abs(e.position - self.verb.position) <= 3
                            and not e.conflicts_with(self.subject, self.od, self.oi, self.regimen),
                            self.entities)
        if candidates:
            self.evidence += "\nequative: 2"
            return sorted(candidates, key=lambda e: e.position)[0]

        return None

    def get_adjuncts(self):
        candidates = []
        for e in self.entities:
            conflict = False
            for x in [self.subject, self.od, self.oi, self.regimen, self.equative]:
                if x != None and e.words[0].position == x.words[0].position:
                    conflict = True
                    break
            if not conflict: candidates.append(e)
        return candidates

    def __str__(self):
        output = "\ninput_sentence: %s" % self.input_sentence.encode('utf-8')
        output += "\n\nentities:\n%s" % '\n'.join([e.__str__() + " " + str(e.msi) + " " + str(e.label) + " " + str(e.level) for e in self.entities])
        output += "\n\nsubject: %s" % self.subject.__str__()
        output += "\nallowed boxes: %s" % [k for (k,v) in filter(lambda (k, v): v is True, self.boxes.iteritems())]
        output += "\n\nverb: %s" % self.boxes['verb'].__str__()
        output += "\nverb_transitivity: %s" % self.verb_transitivity
        output += "\nverb_script_class: %s" % self.verb_script_class
        output += "\n\nod: %s" % self.od.__str__()
        output += "\noi: %s" % self.oi.__str__()
        output += "\nregimen: %s" % self.regimen.__str__()
        output += "\nequative: %s" % self.equative.__str__()
        output += "\nadjuncts: %s\n" % ' '.join([adjunct.__str__() for adjunct in self.adjuncts])
        return output