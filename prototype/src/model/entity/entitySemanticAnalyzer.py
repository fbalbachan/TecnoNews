# -*- coding: utf-8 -*-
from src.ling.gender import Gender
from src.utils.genderDetection.genderDetector import GenderDetector
from src.utils.resources import instance as resources

class EntitySemanticAnalyzer:
    def __init__(self, global_context={}):
        self.global_context = global_context

    def analyze(self, entity):
        if "persons" not in self.global_context:
            self.global_context["persons"] = []

        for method in [self.detect_gender_if_necessary,
                       self.fix_semantic_classification,
                       self.fix_invalid_ne,
                       self.fix_place_classification,
                       self.fix_org_classification,
                       self.fix_person_classification,
                       self.set_names_for_person,
                       self.set_attrs_for_org ]:
            method(entity)

        if "semantic_classification" in entity.msi:
            if entity.msi["semantic_classification"] == "person":
                self.global_context["persons"].append(entity)

    def fix_invalid_ne(self, entity):
        if entity.lexical_form.lower() in self.invalid_name_entities:
            entity.msi["semantic_classification"] = None
            if entity.category() == "noun":
                entity.msi["type"] = "common"

    def fix_person_classification(self, entity):
        if entity.kernel and any( (word in self.org_sufixes for word in entity.kernel.original_components()) ):
            entity.msi["semantic_classification"] = "organization"

    def set_attrs_for_org(self, entity):
        msi = entity.msi
        if msi["semantic_classification"] == "organization" and entity.kernel:
            for word in entity.kernel.original_components():
                if word in self.org_sufixes: attribute = "type"
                else: attribute = "names"

                if not attribute in entity.attributes: entity.attributes[attribute] = []
                entity.attributes[attribute].append(word)

    def fix_semantic_classification(self, entity):
        msi = entity.msi
        if not "semantic_classification" in msi:
            msi["semantic_classification"] = None

    def set_names_for_person(self, entity):
        msi = entity.msi
        if msi["semantic_classification"] == "person" and entity.kernel:
            for word in entity.kernel.original_components():
                if word in self.honorific_prefixes:
                    attribute = "honorifics"
                elif word.lower() in self.person_classes:
                    attribute = "class"
                elif self.gender_detector.gender_of(word):
                    attribute = "names"
                else:
                    attribute = "surnames"

                if not attribute in entity.attributes: entity.attributes[attribute] = []
                entity.attributes[attribute].append(word)


    def fix_place_classification(self, entity):
        msi = entity.msi
        if msi["semantic_classification"] == "place" and entity.kernel:
            words = entity.kernel.components()
            for a_person in self.global_context["persons"]:
                if "surnames" in a_person.attributes:
                    msi["semantic_classification"] = "person"


    def fix_org_classification(self, entity):
        msi = entity.msi
        if msi["semantic_classification"] == "organization" and entity.kernel:
            words = entity.kernel.components()

            if any((word.lower() in self.place_classes for word in words)):
                msi["semantic_classification"] = "place"
            elif any(( word.lower() in self.person_classes for word in words)):
                msi["semantic_classification"] = "person"

            if msi["semantic_classification"] != "organization": return
            if words[0] not in self.honorific_prefixes: return

            if any((self.gender_detector.gender_of(word) for word in words)):
                msi["semantic_classification"] = "person"

    def detect_gender_if_necessary(self, entity):
        if not (entity.category() == "noun" and entity.msi["type"] == "proper" and entity.gender() == Gender.neutral):
            return

        for word in entity.words():
            gender = self.gender_detector.gender_of(word)
            if gender in [Gender.masculine, Gender.feminine]:
                entity.msi["gender"] = gender
                return

    gender_detector = GenderDetector()

    honorific_prefixes = resources.get_wordlist("resources", "honorific_prefs")
    org_sufixes = resources.get_wordlist("resources", "organization_sufs")

    place_classes = resources.get_wordlist("resources", "place_classes")
    person_classes = resources.get_wordlist("resources", "person_classes")

    invalid_name_entities = {name.lower() for name in resources.parse_csv_in("nec", "invalid_ne") }
