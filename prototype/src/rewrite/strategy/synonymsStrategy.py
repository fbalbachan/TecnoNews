# -*- coding: utf-8 -*-
from src.rewrite.rewrite import Rewrite
from src.utils.stringUtils import set_first_letter_case

import csv
import ConfigParser
import re

class SynonymsStrategy:
    def __init__(self, ontology):
        self.ontology = ontology
        self.synonyms = self._get_synonyms()
        self.adverbs = self._get_adverbs()
        self.locucions = self._get_locucions()

    def applies_to(self, clause):
        for leaf in clause.proper_leaves():
            if (leaf.lemma in self.synonyms.keys() or 
                leaf.lexical_form in self.adverbs.keys()):
                return True
        return False

    def rewrite(self, clause):
        ontology = self.ontology

        rewrites = []
        for leaf in clause.proper_leaves():
            if leaf.lemma in self.synonyms.keys():
                synonym = self.synonyms[leaf.lemma]
                replacement = None
                if '_' in synonym or synonym not in ontology.concepts:
                    if synonym in self.locucions and self.locucions[synonym]:
                        pass
                    replacement = synonym.replace('_', ' ')
                else:
                    concept = ontology.concept(synonym)
                    leaf_msi = self._msi_transform(leaf.msi)
                    lexical_forms = [form for form in concept.lexical_forms if  leaf_msi == self._msi_transform(form.msi)]
                    if lexical_forms:
                        replacement = lexical_forms[0].text
                if replacement:
                    rewrites.append(Rewrite.preserving_case(leaf, replacement))
            elif leaf.lexical_form in self.adverbs.keys():
                adverb = self.adverbs[leaf.lexical_form]
                rewrites.append(Rewrite.preserving_case(leaf, adverb.replace('_', ' ')))
                
        return rewrites

    def _get_synonyms(self):
        return self._get_replacements_from_csv("synonyms")

    def _get_adverbs(self):
        return self._get_replacements_from_csv("adverb_forms")

    def _get_replacements_from_csv(self, resource):
        # Warning, it is a dict, it doesn't work for multiple
        # replacements for the same word.

        replacements = {}
        Config = ConfigParser.ConfigParser()
        Config.read("config")
        replacements_filename =  Config.get("resources", resource)
        for line in csv.reader(open(replacements_filename, 'r')):
            replacements[line[0]] = line[1]
            replacements[line[1]] = line[0]
        return replacements
    
    def _get_locucions(self):
        locucions = {}
        Config = ConfigParser.ConfigParser()
        Config.read("config")
        locucions_filename =  Config.get("resources", "locucions")
        regex = re.compile('<.[^_]+>')
        for line in open(locucions_filename, 'r'):
            line = line.strip().split()
            locucions[line[1]] = [y[1:-1] for y in regex.findall(line[0])]
        return locucions

    def _msi_transform(self, msi):
        result_msi = {}
        if 'number' in msi: result_msi['number'] =  msi['number']
        if 'gender' in msi: result_msi['gender'] =  msi['gender']

        if msi['category'] == 'adjective':
            if 'grade' in msi: result_msi['grade'] =  msi['grade']
        elif msi['category'] == 'verb':
            if 'mode' in msi: result_msi['mode'] =  msi['mode']
            if 'person' in msi: result_msi['person'] =  msi['person']
            if 'time' in msi: result_msi['time'] =  msi['time']
        result_msi['category'] = msi['category']
        return result_msi

    type = "replacement"
