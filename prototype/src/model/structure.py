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
        if not self.children: self.is_leaf = True

    def get_head(self):
        entity_head_labels = head_labels
        if self.label == 'grup-verb-inf': entity_head_labels += grup_verb_inf_head_labels

        children_per_level = [(level, list(children)) for (level, children) in groupby(sorted(self.children, key=lambda c: c.level),
                                                                                       key=lambda c: c.level)]
        
        leaves_per_level = [(level, filter(lambda child: child.is_leaf, children)) for (level, children) in children_per_level]
        # print "leaves_per_level", leaves_per_level

        head_candidates = []

        # for (level, children) in children_per_level:
        #     for entity_head_label in entity_head_labels:
        #         # print "revisando entity_head_label: ", entity_head_label
        #         for child in children:
        #             # print "revisando child: ", child, child.label, child.level
        #             if (child.label == entity_head_label):

        #                 # exceptional case
        #                 # print "comparing", child.label, entity_head_label
        #                 # print "child msi", child.msi
        #                 if child.msi["number"] == u"invariable" or child.msi["gender"] == u"common":
        #                     head_candidates.append(child); print "saved head candidate"
        #                     print "invariable or common:", child, child.msi
        #                 else:
        #                     # general case
        #                     if child.label == entity_head_label: return child

        for (level, leaves) in leaves_per_level:
            for entity_head_label in entity_head_labels:
                # print "revisando entity_head_label: ", entity_head_label
                for leaf in leaves:
                    print entity_head_label, " comparando con leaf: ", leaf.__repr__(), leaf.label, leaf.level
                    if (leaf.label == entity_head_label):
                        print "label match", leaf.label, leaf.msi, entity_head_label

                        # exceptional case
                        if leaf.msi["number"] == u"invariable" or leaf.msi["gender"] == u"common":
                            head_candidates.append(leaf); print "saved head candidate"
                            print "invariable or common:", leaf, leaf.msi
                        else:
                            # general case
                            print "not invariable nor common:", leaf, leaf.msi
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
