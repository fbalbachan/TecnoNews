# -*- coding: utf-8 -*-
from src.utils.genderDetection.genderDetector import GenderDetector

class EntityMSISeer:
    def msi_of(self, entity):
        label = entity.node.label
        msi = self.msi_seer_by_label[label](self, entity.node) if label in self.msi_seer_by_label else {}
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

    def msi_of_single_nominal_node(self, node):
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

        if useful_leaves:
            additional_msi = useful_leaves[0].msi
            msi["gender"] = additional_msi["gender"]
            msi["number"] = additional_msi["number"]

        return msi

    def msi_of_coordinated_nominal_node(self, node):
        msi = { "category" : "noun", "number" : "plural", "type" : None }

        pronouns = sorted(node.leaves_of_category("pronoun"), key=lambda pronoun: pronoun.msi["person"])
        msi["person"] = pronouns[0].msi["person"] if pronouns else 3

        genders = [ node.msi["gender"] for node in node.leaves_of_category("noun") + node.leaves_of_category("pronoun")]
        if "masculine" in genders:
            gender = "masculine"
        elif all(map(lambda gender: gender == "feminine", genders)):
            gender = "feminine"
        else:
            gender = "neutral"

        msi["gender"] = gender
        return msi

    def msi_of_leaf(self, node):
        return node.leaves()[0].msi

    def msi_of_infinity(self, node):
        return { "category" : "noun", "gender" : "neutral", "person" : 3, "number" : "singular", "type" : None }

    msi_seer_by_label = { "sn" : msi_of_single_nominal_node,
                           "coor-n" : msi_of_coordinated_nominal_node,
                           "patons" : msi_of_leaf,
                           "ptonic" : msi_of_leaf,
                           "grup-verb-inf" : msi_of_infinity }

    gender_detector = GenderDetector()