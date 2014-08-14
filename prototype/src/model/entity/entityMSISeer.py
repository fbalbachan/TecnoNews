# -*- coding: utf-8 -*-
from ConfigParser import ConfigParser
from os.path import join

from src.utils.genderDetection.genderDetector import GenderDetector


def load_honorific_prefixes():
    config = ConfigParser()
    config.read("config")
    _file = open(dict(config.items("resources"))["honorific_prefs"])
    return [ pref.strip("\n") for pref in list(_file) ]

class EntityMSISeer:
    def msi_of(self, entity):
        label = entity.node.label
        msi = self.msi_seer_by_label[label](self, entity) if label in self.msi_seer_by_label else {}

        self.detect_gender_if_necessary(msi, entity)

        self.fix_semantic_classification(msi)
        self.fix_org_classification(msi, entity)
        self.set_names_for_person(msi, entity)

        return msi

    def fix_semantic_classification(self, msi):
        if not "semantic_classification" in msi: msi["semantic_classification"] = None

    def set_names_for_person(self, msi, entity):
        if msi["semantic_classification"] == "person" and entity.kernel:
            for word in entity.kernel.components():
                if word in self.honorific_prefixes: attribute = "honorifics"
                elif EntityMSISeer.gender_detector.gender_of(word): attribute = "names"
                else: attribute = "surnames"

                if not attribute in entity.attributes: entity.attributes[attribute] = []
                capitalized = word[0].upper() + word[1:]
                entity.attributes[attribute].append(capitalized)

    def fix_org_classification(self, msi, entity):
        if msi["semantic_classification"] == "organization" and entity.kernel:
            words = entity.kernel.components()
            if words[0] not in self.honorific_prefixes: return
            if any(( EntityMSISeer.gender_detector.gender_of(word) for word in words)):
                msi["semantic_classification"] = "person"

    def detect_gender_if_necessary(self, msi, entity):
        if not (msi["category"] == "noun" and msi["type"] == "proper" and msi["gender"] == "neutral"): return

        for word in entity.words():
            gender = EntityMSISeer.gender_detector.gender_of(word)
            if gender in [ "masculine", "feminine" ]:
                msi["gender"] = gender
                return

    def msi_of_single(self, entity):
        node = entity.node
        banned_labels = ["grup-sp", "sp-de"]
        banned_nodes = set(filter(lambda child: not child.is_leaf() and child.label in banned_labels, node.children))

        nouns = node.leaves_of_category("noun") + node.leaves_of_category("number")
        if self.has_unexchangeable_appositional_relationship(nouns):
            entity.attributes["class"] = nouns[0].lexical_form
            nouns = [ nouns[1] ]

        useful_leaves = nouns + node.leaves_of_category("pronoun") + node.leaves_of_category("determinant") \
            + node.leaves_of_category("adjective")
        useful_leaves = filter(lambda leaf: not banned_nodes & set(leaf.path_to_root()), useful_leaves)

        useful_leaves.reverse()
        entity.kernel = useful_leaves.pop()
        msi = entity.kernel.msi

        if msi["category"] == "number":
            msi["gender"] = "neutral"
            msi["number"] = "invariable"
            msi["type"] = "common"
            msi["category"] = "noun"

        if not "person" in msi or not msi["person"]: msi["person"] = 3

        self.disambiguate_if_necessary(msi, useful_leaves)

        return msi

    def has_unexchangeable_appositional_relationship(self, kernel_nouns):
        return [ noun.msi["type"] for noun in kernel_nouns ] == [ "common", "proper" ]

    def disambiguate_if_necessary(self, msi, leaves):
        if not leaves: return
        leaves = leaves[::-1]

        non_neutral_attribute_values = { "gender" : [ "masculine", "feminine"], "number" : [ "singular", "plural"] }

        for attribute, non_neutral_values in non_neutral_attribute_values.items():
            if msi[attribute] not in non_neutral_values:
                for leaf in leaves:
                    if leaf.msi[attribute] in non_neutral_values: msi[attribute] = leaf.msi[attribute]

    def msi_of_coordinated(self, entity):
        msi = { "category" : "noun", "number" : "plural", "type" : None, "semantic_classification" : None }

        pronouns = sorted(entity.children_of_category("pronoun"), key=lambda pronoun: pronoun.msi["person"])
        msi["person"] = pronouns[0].msi["person"] if pronouns else 3

        genders = [ child.msi["gender"] for child in \
                   entity.children_of_category("noun") + entity.children_of_category("pronoun")]
        if "masculine" in genders:
            gender = "masculine"
        elif all(map(lambda gender: gender == "feminine", genders)):
            gender = "feminine"
        else:
            gender = "neutral"

        msi["gender"] = gender
        return msi

    def msi_of_leaf(self, entity):
        node = entity.node
        return node.leaves()[0].msi

    def msi_of_infinity(self, entity):
        return { "category" : "noun", "gender" : None, "person" : 3, "number" : "singular", "type" : None,
                "semantic_classification" : None }

    msi_seer_by_label = {   "sn" : msi_of_single,
                            "grup-nom-ms" : msi_of_single,
                            "grup-nom-fs" : msi_of_single,
                            "grup-nom-mp" : msi_of_single,
                            "grup-nom-fp" : msi_of_single,
                            "coor-n" : msi_of_coordinated,
                            "patons" : msi_of_leaf,
                            "ptonic" : msi_of_leaf,
                            "grup-verb-inf" : msi_of_infinity }

    gender_detector = GenderDetector()
    honorific_prefixes = load_honorific_prefixes()
