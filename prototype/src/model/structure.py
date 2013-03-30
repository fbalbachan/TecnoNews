#!/usr/bin/python
# -*- coding: utf-8 -*-
import re, copy
from word import *
from itertools import izip, groupby
from ling.msi_mapper import *
from ling.head_labels import *
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
        self.msi = empty_msi
        self.children = []
        self.is_leaf = False

    def __repr__(self):
        return u"%s (%d,%d) %s [%d]" % (self.label,
                                        self.start,
                                        self.end,
                                        ' '.join([w.form for w in self.words]),
                                        self.level)

    def __str__(self):
        return ' '.join([x for x in self.forms()])

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

    def assign_msi(self):
        if self.is_leaf: return

        entity_head_labels = head_labels
        if self.label == 'grup-verb-inf': entity_head_labels += grup_verb_inf_head_labels

        children_per_level = [(level, list(children)) for (level, children) in groupby(sorted(self.children, key=lambda c: c.level),
                                                                                       key=lambda c: c.level)]
        
        leaves_per_level = [(level, filter(lambda child: child.is_leaf, children)) for (level, children) in children_per_level]
        # print("leaves_per_level", leaves_per_level)

        all_leaves = []
        for (level, leaves) in leaves_per_level:
            all_leaves += filter(lambda leaf: leaf.words[0].tag != "CC", leaves)

        head_candidates = []

        # exceptional caso: coor-n                         TODO género (con la 1° involucrada o no)
        if self.label == 'coor-n':
            # son todas feminine => feminine; else masculine

            # set number
            self.msi['number'] = u'plural'

            # set gender
            all_feminine = all([leaf.msi["gender"] == u"feminine" for leaf in all_leaves])
            any_masculine = any([leaf.msi["gender"] == u"masculine" for leaf in all_leaves])
            print all_feminine
            if any_masculine:
                self.msi['gender'] = u'masculine'
            if all_feminine:
                self.msi['gender'] = u'feminine'
            else:
                self.msi['gender'] = u'neutral'
            print self.msi

            # set person
            any_1_person = any([leaf.msi["person"] == 1 for leaf in all_leaves])
            any_2_person = any([leaf.msi["person"] == 2 for leaf in all_leaves])
            if any_1_person:
                self.msi['person'] = 1
            elif any_2_person:
                self.msi['person'] = 2
            else:
                self.msi['person'] = 3

            return

        for (level, leaves) in leaves_per_level:
            for entity_head_label in entity_head_labels:
                for leaf in leaves:
                    if (leaf.label == entity_head_label):
                        # print(leaf, leaf.words[0].tag, "label match", leaf.label, leaf.msi, leaf.full_msi, entity_head_label)

                        # exceptional case
                        if leaf.msi["number"] == u"invariable" or leaf.msi["gender"] == u"common":
                            head_candidates.append(leaf); # print("saved head candidate (invariable or common):", leaf, leaf.msi)

                        # general case
                        else:
                            self.msi = leaf.msi


        if head_candidates:
            # found exceptional head
            self.msi = head_candidates[0].msi
        else:
            # there is no head
            return

    def get_msi(self):
        # if not self.full_msi: self.full_msi = tag2fullmsi(self.words[0].tag)
        return msi(self.full_msi)

# def get_empty_structure():
#     return Structure((0, 0, ['empty_[', u'+(x x EMPTY -){0', ']'], 0))

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
