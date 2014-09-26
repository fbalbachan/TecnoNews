# -*- coding: utf-8 -*-
from src.rewrite.rewrite import Rewrite
from src.utils.stringUtils import set_first_letter_case

import csv
import ConfigParser

class SynonymsStrategy:
    def __init__(self, ontology):
        self.ontology = ontology
        self.synonyms = self._get_synonyms()

    def applies_to(self, clause):
        for leaf in clause.proper_leaves():
            if leaf.lemma in self.synonyms.keys():
                return True
        return False

    def rewrite(self, clause):
        ontology = self.ontology

        rewrites = []
        for leaf in clause.proper_leaves():
            if leaf.lemma in self.synonyms.keys():
                synonym = self.synonyms[leaf.lemma]
                concept = ontology.concept(synonym)
                leaf_msi = self._msi_transform(leaf.msi)
                lexical_forms = [form for form in concept.lexical_forms if  leaf_msi == self._msi_transform(form.msi)]
                if lexical_forms:
                    rewrites.append(Rewrite.preserving_case(leaf, lexical_forms[0].text))
        return rewrites

    def _get_synonyms(self):
        # Warning, it is a dict, it doesn't work for multiple
        # synonyms ofr the same word.

        synonyms = {}
        Config = ConfigParser.ConfigParser()
        Config.read("config")
        synonyms_filename =  Config.get("resources", "synonyms")
        for line in csv.reader(open(synonyms_filename, 'r')):
            synonyms[line[0]] = line[1]
            synonyms[line[1]] = line[0]
        return synonyms

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


 

 
