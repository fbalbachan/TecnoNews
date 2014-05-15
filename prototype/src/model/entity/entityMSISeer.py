# -*- coding: utf-8 -*-
from src.utils.genderDetection.genderDetector import GenderDetector

class EntityMSISeer:
    def msi_of(self, entity):
        label = entity.node.label
        msi = self.msi_seer_by_label[label](self, entity) if label in self.msi_seer_by_label else {}
        self.detect_gender_if_necessary(msi, entity)
        return msi

    def detect_gender_if_necessary(self, msi, entity):
        if not (msi["category"] == "noun" and msi["type"] == "proper" and msi["gender"] == "neutral"): return
        words = entity.lexical_form.split("_")
        genders = [ EntityMSISeer.gender_detector.gender_of(word) for word in words ]
        for gender in [ "masculine", "feminine" ]:
            if gender in genders:
                msi["gender"] = gender
                return

    def msi_of_single(self, entity):
        node = entity.node
        banned_labels = ["grup-sp", "sp-de"]
        banned_nodes = set(filter(lambda child: not child.is_leaf() and child.label in banned_labels, node.children))

        nouns = node.leaves_of_category("noun")
        useful_leaves = nouns + node.leaves_of_category("pronoun") + node.leaves_of_category("determinant") \
            + node.leaves_of_category("adjective")
        useful_leaves = filter(lambda leaf: not banned_nodes & set(leaf.path_to_root()), useful_leaves)

        useful_leaves.reverse()
        msi = useful_leaves.pop().msi

        if not "person" in msi or not msi["person"]: msi["person"] = 3
        if nouns: msi["category"] = "noun"

        self.disambiguate_if_necessary(msi, useful_leaves)

        return msi

    def disambiguate_if_necessary(self, msi, leaves):
        if not leaves: return
        leaves = leaves[::-1]

        non_neutral_attribute_values = { "gender" : [ "masculine", "feminine"], "number" : [ "singular", "plural"] }

        for attribute, non_neutral_values in non_neutral_attribute_values.items():
            if msi[attribute] not in non_neutral_values:
                for leaf in leaves:
                    if leaf.msi[attribute] in non_neutral_values: msi[attribute] = leaf.msi[attribute]

    def msi_of_coordinated(self, entity):
        msi = { "category" : "noun", "number" : "plural", "type" : None }

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
        return { "category" : "noun", "gender" : None, "person" : 3, "number" : "singular", "type" : None }

    msi_seer_by_label = { "sn" : msi_of_single,
                           "coor-n" : msi_of_coordinated,
                           "patons" : msi_of_leaf,
                           "ptonic" : msi_of_leaf,
                           "grup-verb-inf" : msi_of_infinity }

    gender_detector = GenderDetector()