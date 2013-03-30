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
        self.msi = None
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

    def assign_head(self):
        self.head = self.get_head()
        if self.head:
            self.msi = self.head.msi
            self.full_msi = self.head.full_msi
        else:
            self.msi = empty_msi

    def get_head(self):
        if self.is_leaf: return self

        entity_head_labels = head_labels
        if self.label == 'grup-verb-inf': entity_head_labels += grup_verb_inf_head_labels

        children_per_level = [(level, list(children)) for (level, children) in groupby(sorted(self.children, key=lambda c: c.level),
                                                                                       key=lambda c: c.level)]
        
        leaves_per_level = [(level, filter(lambda child: child.is_leaf, children)) for (level, children) in children_per_level]
        # print("leaves_per_level", leaves_per_level)

        head_candidates = []

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
                            return leaf

                # caso coor-n
                # género (con la 1° involucrada o no)

        if head_candidates:
            # found exceptional head
            return head_candidates[0]
        else:
            # there is no head
            return None

    def get_full_msi(self):
        if not self.head: return empty_msi
        return tag2fullmsi(self.head.words[0].tag)

    def get_msi(self):
        if not self.full_msi: self.get_full_msi()
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
