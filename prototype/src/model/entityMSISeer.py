# -*- coding: utf-8 -*-

class EntityMSISeer:
    def msi_of(self, entity):
        label = entity.node.label
        if label in self.msi_seer_by_label:
            return self.msi_seer_by_label[label](self, entity.node)
        else:
            return {}

    def msi_of_single_nominal_node(self, node):
        nouns_and_pronouns = node.leaves_of_category("noun") + node.leaves_of_category("pronoun")
        return sorted(nouns_and_pronouns, key = lambda node: node.level())[0].msi

    def msi_of_coordinated_nominal_node(self, node):
        msi = { "number" : "plural" }

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
        return { "gender" : "neutral", "person" : 3, "number" : "singular" }

    msi_seer_by_label = { "sn" : msi_of_single_nominal_node,
                           "coor-n" : msi_of_coordinated_nominal_node,
                           "patons" : msi_of_leaf,
                           "ptonic" : msi_of_leaf,
                           "grup-verb-inf" : msi_of_infinity }
