#!/usr/bin/python
# -*- coding: utf-8 -*-
import re, copy
from word import *
from itertools import izip, groupby
from ling.msi_mapper import *
from ling.head_labels import *
from utils.logger_utils import *

class Verb(Structure):

    def __init__(self):
        Structure.__init__()

    def assign_msi(self):
        if self.is_leaf: return

        if self.label == 'grup-verb-inf': head_labels.insert(0, grup_verb_inf_head_labels[0])

        children_per_level = [(level, list(children)) for (level, children) in groupby(sorted(self.children, key=lambda c: c.level),
                                                                                       key=lambda c: c.level)]
        
        leaves_per_level = [(level, filter(lambda child: child.is_leaf, children)) for (level, children) in children_per_level]

        msi_candidates = []

        # coor-n case:
        if self.label == 'coor-n':

            # set number
            self.msi["number"] = u'plural'

            all_leaves = []
            for (level, leaves) in leaves_per_level:
                all_leaves += filter(lambda leaf: leaf.words[0].tag != "CC", leaves)

            # set gender
            any_masculine = any([leaf.msi["gender"] == u"masculine" for leaf in all_leaves])
            all_feminine = all([leaf.msi["gender"] == u"feminine" for leaf in all_leaves])
            if any_masculine: self.msi["gender"] = u'masculine'
            elif all_feminine: self.msi["gender"] = u'feminine'
            else: self.msi["gender"] = u'neutral'

            # set person
            any_1_person = any([leaf.msi["person"] == 1 for leaf in all_leaves])
            any_2_person = any([leaf.msi["person"] == 2 for leaf in all_leaves])
            if any_1_person: self.msi["person"] = 1
            elif any_2_person: self.msi["person"] = 2
            else: self.msi["person"] = 3

            return

        for (level, leaves) in leaves_per_level:
            for entity_head_label in head_labels:
                for leaf in leaves:
                    if (leaf.label == entity_head_label):

                        # [invariable|common] case
                        if leaf.msi["number"] == u"invariable" or leaf.msi["gender"] == u"common":
                            msi_candidates.append(leaf)

                        # general case
                        else:
                            self.msi = leaf.msi
                            return

        if msi_candidates: self.msi = msi_candidates[0].msi