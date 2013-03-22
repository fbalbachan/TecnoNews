#!/usr/bin/python
# -*- coding: utf-8 -*-
import re, copy
from word import *
from conf import *
from itertools import izip

class Structure(object):
    def __init__(self, (start, end, struct, nivel)):
        self.label = struct[0].split('_[')[0].strip('+').lower()
        self.start = start
        self.end = end
        self.struct = struct
        self.nivel = nivel
        self.msi = None # <- núcleo.msi
        self.words = [Word(match.strip()) for match in re.findall(r'.\(\w+ \w+ [A-Z0-9]+ -\){-?\d+', ' '.join(struct), re.U)]
        self.children = []

    def __repr__(self):
        return u"%s (%d,%d) %s [%d]" % (self.label, # .encode('utf-8')
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
            return container
        else:
            return self

    def head(self):
        # TODO: guardar sólo labels; atributos salen del mapeador de msi
        labels_de_head = labels_de_head_de_sn

        # núcleo de grup-verb-inf es especial:
        if self.label == 'grup-verb-inf':
            head_labels += grup_verb_inf_head_labels

        for child in sorted(self.children, key=lambda c: c.nivel):
            for head_label in head_labels:
                if child.label == head_label[0]:
                    (label, genero, numero) = head_label[0], head_label[1], head_label[2]
                    return child, (label, genero, numero)
                    
        return get_empty_structure(), ('', '', '')

def get_empty_structure():
    return Structure((0, 0, ['empty_[', u'+(x x EMPTY -){0', ']'], 0))
