# -*- coding: utf-8 -*-

class EntityMSISeer:
    def msi_of(self, entity):
        label = entity.node.label
        if label in self.msi_seer_by_label:
            return self.msi_seer_by_label[label](self, entity.node)
        else:
            return {}

    def msi_of_single_nominal_node(self, node):
        banned_nodes = set(filter(lambda child: not child.is_leaf() and child.label in ["grup-sp"], node.children))

        nouns = node.leaves_of_category("noun")
        useful_leaves = nouns + node.leaves_of_category("pronoun") + node.leaves_of_category("determinant")
        useful_leaves = filter(lambda leaf: not banned_nodes & set(leaf.path_to_root()), useful_leaves)

        msi = useful_leaves[0].msi
        if not "person" in msi or not msi["person"]: msi["person"] = 3
        if nouns: msi["category"] = "noun"

        return msi

    def msi_of_coordinated_nominal_node(self, node):
        msi = { "category" : "noun", "number" : "plural" }

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
        return { "category" : "noun", "gender" : "neutral", "person" : 3, "number" : "singular" }

    msi_seer_by_label = { "sn" : msi_of_single_nominal_node,
                           "coor-n" : msi_of_coordinated_nominal_node,
                           "patons" : msi_of_leaf,
                           "ptonic" : msi_of_leaf,
                           "grup-verb-inf" : msi_of_infinity }
