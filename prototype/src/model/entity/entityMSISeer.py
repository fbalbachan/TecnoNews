# -*- coding: utf-8 -*-

class EntityMSISeer:
    def msi_of(self, entity):
        label = entity.node.label
        msi = self.msi_seer_by_label[label](self, entity) if label in self.msi_seer_by_label else {}
        return msi

    def msi_of_single(self, entity):
        node = entity.node

        banned_labels = ["grup-sp", "sp-de"]
        banned_nodes = set(filter(lambda child: not child.is_leaf() and child.label in banned_labels, node.children))

        nouns = self.filter_banned(node.leaves_of_category("noun") + node.leaves_of_category("number"), banned_nodes)
        if self.has_unexchangeable_appositional_relationship(nouns):
            entity.attributes["class"] = [ nouns[0].lexical_form ]
            nouns = [ nouns[1] ]

        other_leaves = node.leaves_of_category("pronoun", "determinant", "adjective")
        useful_leaves = nouns + self.filter_banned(other_leaves, banned_nodes)

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

    def filter_banned(self, leaves, banned_nodes):
        return filter(lambda leaf: not banned_nodes & set(leaf.path_to_root()), leaves)

    def has_unexchangeable_appositional_relationship(self, kernel_nouns):
        return [ noun.msi["type"] if "type" in noun.msi else None for noun in kernel_nouns ] == [ "common", "proper" ]

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
