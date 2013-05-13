#!/usr/bin/python
# -*- coding: utf-8 -*-
import re, copy
from word import *
from itertools import izip, groupby
from ling.msi_mapper import *
from ling.head_labels import *
from ling.verb_categories import *
from ling.entity_labels import *
from utils.logger_utils import *

class Structure(object):
    def __init__(self, (start, end, struct, level)):
        self.logger = get_logger('entinews')

        self.words = [Word(match.strip()) for match in re.findall(r'.\(\w+ \w+ [A-Z0-9]+ -\){-?\d+', ' '.join(struct), re.U)]
        self.label = struct[0].split('_[')[0].strip('+').lower()
        self.start = start
        self.end = end
        self.struct = struct
        self.level = level
        self.head = None
        self.full_msi = None
        self.msi = {}
        self.children = []
        self.is_leaf = False
        self.lemma = None
        self.position = None
        self.entity_type = None

    def __repr__(self):
        return u'%s (%d,%d) %s [%d]' % (self.label,
                                        self.start,
                                        self.end,
                                        u' '.join([w.form for w in self.words]),
                                        self.level)#.encode('utf-8')

    def __str__(self):
        return u' '.join([x for x in self.forms()]).encode('utf-8')

    def forms(self):
        return [word.form for word in self.words]

    def contains(self, another_structure):
        return (self.start < another_structure.start) and (self.end >= another_structure.end) 

    def contains_any(self, iterable):
        return any(self.contains(i) for i in iterable)

    def is_contained_by(self, another_structure):
        return another_structure.contains(self)

    def is_contained_by_any(self, iterable):
        return any(i.contains(self) for i in iterable)

    def set_leaf_status(self):
        if not self.children: self.is_leaf = True

    # def has_multiple_children(self):
    #     immediate_children = [child for child in self.children if child.level == self.level + 1]
    #     return len(immediate_children) > 1

    def get_children_per_level(self, n):
        return sorted(filter(lambda child: child.level == n, self.children), key=lambda c: c.position)

    def is_proper_entity(self):
        return self.label in proper_entity_labels

    def is_pronominal_entity(self):
        return self.label in pronominal_entity_labels

    def assign_entity_type(self):
        if self.is_proper_entity():
            self.entity_type = 'proper_entity'
        elif self.is_pronominal_entity():
            self.entity_type = 'pronominal_entity'            

    def has_modal_verb(self):
        return len(self.words) > 1 and (self.words[0].lemma in modal_verbs)

    def is_impersonal_verb(self):
        return self.lemma in impersonal_verbs

    def is_existential_verb(self):
        return self.lemma == existential_verb

    def assign_verb_lemma(self):
        self.lemma = self.words[-1].lemma

    def assign_verb_position(self):
        self.position = self.words[-1].position

    def assign_verb_msi(self):
        if self.has_modal_verb(): self.msi = msi(tag2fullmsi(self.words[0].tag)); return
        if not(self.is_leaf): self.msi = self.children[0].msi; return
        if self.is_impersonal_verb(): self.msi['person'] = 0; return
        if self.is_existential_verb(): self.msi['number'] = u'invariable'; return

    def assign_verb_pass_lemma(self):
        self.lemma = filter(lambda child: child.label == 'parti-flex', self.children)[0].children[0].words[0].lemma 

    def assign_verb_pass_msi(self):
        if not(self.is_leaf):
            vauxs = filter(lambda child: child.label == 'vaux', self.children)
            vsers = filter(lambda child: child.label == 'vser', self.children)
            if vauxs:
                self.msi = vauxs[0].msi
            elif vsers:
                self.msi = vsers[0].msi

    def assign_noun_msi(self):
        if self.is_leaf: return

        if self.label == 'grup-verb-inf': head_labels.insert(0, grup_verb_inf_head_labels[0])

        children_per_level = [(level, list(children)) for (level, children) in groupby(sorted(self.children, key=lambda c: c.level),
                                                                                       key=lambda c: c.level)]
        
        leaves_per_level = [(level, filter(lambda child: child.is_leaf, children)) for (level, children) in children_per_level]

        msi_candidates = []

        # coor-n case:
        if self.label == 'coor-n':

            # set number
            self.msi['number'] = u'plural'

            all_leaves = []
            for (level, leaves) in leaves_per_level:
                all_leaves += filter(lambda leaf: leaf.words[0].tag != 'CC', leaves)

            # set gender
            any_masculine = any([leaf.msi['gender'] == u'masculine' for leaf in all_leaves])
            all_feminine = all([leaf.msi['gender'] == u'feminine' for leaf in all_leaves])
            if any_masculine: self.msi['gender'] = u'masculine'
            elif all_feminine: self.msi['gender'] = u'feminine'
            else: self.msi['gender'] = u'neutral'

            # set person
            any_1_person = any([leaf.msi['person'] == 1 for leaf in all_leaves])
            any_2_person = any([leaf.msi['person'] == 2 for leaf in all_leaves])
            if any_1_person: self.msi['person'] = 1
            elif any_2_person: self.msi['person'] = 2
            else: self.msi['person'] = 3

            return

        for (level, leaves) in leaves_per_level:
            for entity_head_label in head_labels:
                for leaf in leaves:
                    if (leaf.label == entity_head_label):

                        # [invariable|common] case
                        if leaf.msi['number'] == u'invariable' or leaf.msi['gender'] == u'common':
                            msi_candidates.append(leaf)

                        # general case
                        else:
                            self.msi = leaf.msi
                            return

        if msi_candidates: self.msi = msi_candidates[0].msi


def build_structure(word=u'_', label=u'TACIT'):
    leaf = u'+(%s %s %s -){0' % (word, word, label)
    struct = [u'%s_[' % label, leaf, ']']
    return Structure((0, 0, struct, 0))

def estructuras_balanceadas(lista):
    w = 0
    out = []
    level = 0
    # set position for each word
    for x in lista:
        if x.startswith('+(') or x.startswith('('):
            w += 1
            out.append(x+'{%d'%w)
        else:
            out.append(x)
    lista = out
    # parse bracketed structures
    stack = []
    for i, x in enumerate(lista):
        if x.endswith(']') and stack:
            start = stack.pop()
            level -= 1
            yield (start, i, lista[start:i+1], level) # (start, end, structure, level)
        elif x.endswith('_['):
            stack.append(i)
            level += 1
