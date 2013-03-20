#!/usr/bin/python
# -*- coding: utf-8 -*-
import re, copy
from palabra import *
from conf import *
from itertools import izip

class Estructura(object):
    def __init__(self, (start, end, struct, nivel)):
        self.label = struct[0].split('_[')[0].strip('+').lower()
        self.start = start
        self.end = end
        self.struct = struct
        self.nivel = nivel
        self.msi = None # <- núcleo.msi
        self.words = [Palabra(match.strip()) for match in re.findall(r'.\(\w+ \w+ [A-Z0-9]+ -\){-?\d+', ' '.join(struct), re.U)]
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

    def contains(self, otra_estructura):
        return (self.start < otra_estructura.start) and (self.end >= otra_estructura.end) 

    def contains_any(self, iterable):
        return any(self.contains(i) for i in iterable)

    def is_contained_by(self, otra_estructura):
        return otra_estructura.contains(self)

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

    def nucleo(self):
        # TODO: guardar sólo labels; atributos salen del mapeador de msi
        labels_de_nucleo = labels_de_nucleo_de_sn

        # núcleo de grup-verb-inf es especial:
        if self.label == 'grup-verb-inf':
            labels_de_nucleo += labels_de_nucleo_de_grup_verb_inf

        for child in sorted(self.children, key=lambda c: c.nivel):
            for label_de_nucleo in labels_de_nucleo:
                if child.label == label_de_nucleo[0]:
                    (label, genero, numero) = label_de_nucleo[0], label_de_nucleo[1], label_de_nucleo[2]
                    return child, (label, genero, numero)
                    
        return get_estructura_vacia(), ('', '', '')

def get_estructura_vacia():
    return Estructura((0, 0, ['empty_[', u'+(x x EMPTY -){0', ']'], 0))
