# -*- coding: utf-8 -*-
from ConfigParser import ConfigParser

from src.utils.genderDetection.genderDetector import GenderDetector


def load_honorific_prefixes():
    config = ConfigParser()
    config.read("config")
    _file = open(dict(config.items("resources"))["honorific_prefs"])
    return [ pref.strip("\n") for pref in list(_file) ]

class EntitySemanticAnalyzer:
    def analyze(self, entity):
        for method in [self.detect_gender_if_necessary, self.fix_semantic_classification, self.fix_org_classification,
                       self.set_names_for_person]:
            method(entity)

    def fix_semantic_classification(self, entity):
        msi = entity.msi
        if not "semantic_classification" in msi: msi["semantic_classification"] = None

    def set_names_for_person(self, entity):
        msi = entity.msi
        if msi["semantic_classification"] == "person" and entity.kernel:
            for word in entity.kernel.original_components():
                if word in self.honorific_prefixes: attribute = "honorifics"
                elif self.gender_detector.gender_of(word): attribute = "names"
                else: attribute = "surnames"

                if not attribute in entity.attributes: entity.attributes[attribute] = []
                entity.attributes[attribute].append(word)

    def fix_org_classification(self, entity):
        msi = entity.msi
        if msi["semantic_classification"] == "organization" and entity.kernel:
            words = entity.kernel.components()
            if words[0] not in self.honorific_prefixes: return
            if any(( self.gender_detector.gender_of(word) for word in words)):
                msi["semantic_classification"] = "person"

    def detect_gender_if_necessary(self, entity):
        msi = entity.msi
        if not (msi["category"] == "noun" and msi["type"] == "proper" and msi["gender"] == "neutral"): return

        for word in entity.words():
            gender = self.gender_detector.gender_of(word)
            if gender in [ "masculine", "feminine" ]:
                msi["gender"] = gender
                return

    gender_detector = GenderDetector()
    honorific_prefixes = load_honorific_prefixes()
