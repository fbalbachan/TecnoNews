#!/usr/bin/python
# -*- coding: utf-8 -*-
import re, copy
from word import *
from itertools import izip, groupby
from ling.msi_mapper import *
from ling.head_labels import *
from utils.logger_utils import *

class Structure(object):
    def __init__(self, (start, end, struct, nivel)):
        self.logger = get_logger('entinews')

        self.words = [Word(match.strip()) for match in re.findall(r'.\(\w+ \w+ [A-Z0-9]+ -\){-?\d+', ' '.join(struct), re.U)]
        self.label = struct[0].split('_[')[0].strip('+').lower()
        self.start = start
        self.end = end
        self.struct = struct
        self.nivel = nivel
        self.head = None
        self.full_msi = None
        self.msi = None
        self.children = []

    def __repr__(self):
        return u"%s (%d,%d) %s [%d]" % (self.label,
                                        self.start,
                                        self.end,
                                        ' '.join([w.form for w in self.words]),
                                        self.nivel)

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

    def quitar(self, quitables):
        if quitables:
            container = copy.deepcopy(self)
            quitables = filter(lambda x: container.contains(x), quitables)
            if quitables:
                ranges_quitables = sorted([(e.start, e.end) for e in quitables], key=lambda (start,end): start)
                removable_words = [w.position for quitable in quitables for w in quitable.words]

                # children not matching any quitables
                valid_children = [c for c in container.children for r in ranges_quitables if not(any([x for x in range(c.start, c.end+1) if x in range(r[0], r[1]+1)]))]

                # children containing quitables -> remove their matching children
                partially_valid_children = [c for c in container.children if c.contains_any(quitables)]
                for c in partially_valid_children:
                    c.children = filter(lambda x: not((x.start, x.end) in ranges_quitables) and not(x.is_contained_by_any(quitables)), c.children)
                    c.words = [w for w in c.words if w.position not in removable_words]
                    valid_children.append(c)
                
                container.children = set(valid_children)
                container.words = [w for w in container.words if w.position not in removable_words]

                if container.children:
                    nuevo_start = sorted([e.start for e in container.children])[0]
                    nuevo_end = sorted([e.end for e in container.children]).pop()
                    container.start = nuevo_start
                    container.end = nuevo_end
            self.refresh()
            return container
        else:
            self.refresh()
            return self

    def refresh(self):
        self.head = self.get_head()
        self.full_msi = self.get_full_msi()
        self.msi = self.get_msi()

    def get_head(self):
        entity_head_labels = head_labels
        if self.label == 'grup-verb-inf': entity_head_labels += grup_verb_inf_head_labels

        children_per_level = [(level, list(children)) for (level, children) in groupby(sorted(self.children, key=lambda c: c.nivel),
                                                                                       key=lambda c: c.nivel)]

        for (level, children) in children_per_level:
            for entity_head_label in entity_head_labels:
                for child in children:
                    if child.label == entity_head_label: return child

        # found no head
        return None # get_empty_structure()

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
    nivel = 0
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
            nivel -= 1
            yield (start, i, lista[start:i+1], nivel) # (principio, fin, estructura, nivel)
        elif x.endswith('_['):
            stack.append(i)
            nivel += 1
