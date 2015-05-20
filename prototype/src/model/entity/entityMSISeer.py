# -*- coding: utf-8 -*-

import ConfigParser

from src.model.entity.entitySemanticAnalyzer import EntitySemanticAnalyzer
from src.model.entity.animityEnum import AnimityEnum


class EntityMSISeer:

    def __init__(self):
        # TODO: Warning this would be accessing the config file each time an entity is instantiated
        config = ConfigParser.ConfigParser()
        config.read("config")
        self.persons = self._get_items(config, "persons")
        self.demonyms = self._get_items(config, "demonyms")
        self.animals = self._get_items(config, "animals")

    def msi_of(self, entity):
        # print "Entering msi_of"
        label = entity.node.label
        entity.msi = self.msi_seer_by_label[label](self, entity) if label in self.msi_seer_by_label else {}
        semantic_analyzer = EntitySemanticAnalyzer()
        semantic_analyzer.analyze(entity)
        entity.msi["animity"] = self.calculate_animity_for(entity)
        return entity.msi

    def msi_of_single(self, entity):
        node = entity.node

        banned_labels = ["grup-sp", "sp-de"]
        banned_nodes = set(filter(lambda child: not child.is_leaf() and child.label in banned_labels, node.children))

        nouns = self.filter_banned(node.leaves_of_category("noun") + node.leaves_of_category("number"), banned_nodes)
        if self.has_unexchangeable_appositional_relationship(nouns):
            entity.attributes["class"] = [nouns[0].lexical_form]
            nouns = [nouns[1]]

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

        if "person" not in msi or not msi["person"]:
            msi["person"] = 3

        self.disambiguate_if_necessary(msi, useful_leaves)

        return msi

    def filter_banned(self, leaves, banned_nodes):
        return filter(lambda leaf: not banned_nodes & set(leaf.path_to_root()), leaves)

    def has_unexchangeable_appositional_relationship(self, kernel_nouns):
        return [ noun.msi["type"] if "type" in noun.msi else None for noun in kernel_nouns ] == [ "common", "proper" ]

    def disambiguate_if_necessary(self, msi, leaves):
        if not leaves: return
        leaves = leaves[::-1]

        non_neutral_attribute_values = {"gender": ["masculine", "feminine"], "number": ["singular", "plural"]}

        for attribute, non_neutral_values in non_neutral_attribute_values.items():
            if msi[attribute] not in non_neutral_values:
                for leaf in leaves:
                    if leaf.msi[attribute] in non_neutral_values: msi[attribute] = leaf.msi[attribute]

    def msi_of_coordinated(self, entity):
        msi = {"category": "noun", "number": "plural", "type": None, "semantic_classification": None}

        pronouns = sorted(entity.children_of_category("pronoun"), key=lambda pronoun: pronoun.msi["person"])
        msi["person"] = pronouns[0].msi["person"] if pronouns else 3

        genders = [child.msi["gender"]
                   for child in entity.children_of_category("noun") + entity.children_of_category("pronoun")]
        if "masculine" in genders:
            gender = "masculine"
        elif all(map(lambda p_gender: p_gender == "feminine", genders)):
            gender = "feminine"
        else:
            gender = "neutral"

        msi["gender"] = gender

        return msi

    def msi_of_leaf(self, entity):
        msi = entity.node.leaves()[0].msi
        return msi

    def msi_of_infinity(self, entity):
        return {"category": "noun", "gender": None, "person": 3,
                "number": "singular", "type": None, "semantic_classification": None}

    def calculate_animity_for(self, entity):
        default_animity_value = AnimityEnum.inanimate

        # If entity has an animity value, other than the default, then return it (assuming it was previously calculated)
        if "animity" in entity.msi and entity.msi["animity"] is not default_animity_value:
            return entity.msi["animity"]

        # Entities with 1 token being a "paton" or "ptonic"
        elif len(entity.token.components) is 1 and entity.node.label in ["patons", "ptonic"]:
            if entity.msi['person'] in [1, 2]:
                return AnimityEnum.animated

            if entity.msi['person'] is 3 and entity.msi['case'] == "dative":
                return AnimityEnum.animated

            if entity.msi['person'] is 3:
                return AnimityEnum.bianimate

        elif entity.has_attr("implicit") or entity.node.label in ["grup-verb-inf"]:
            return AnimityEnum.inanimate

        elif entity.kernel:
            return self._calculate_animity_single(entity.msi, entity.kernel)

        # (has no kernel, is not a "patons") if it is "coor-n", then look into children animity
        elif entity.node.label is "coor-n":
            for child in entity.children:
                child_animity = self.calculate_animity_for(child)
                # if at least one of the child entities has animity return that
                if child_animity is not default_animity_value:
                    return child_animity

        elif len(entity.children) > 0:
            child = entity.children[0]
            return self.calculate_animity_for(child)

        # other cases
        return default_animity_value

    def _calculate_animity_single(self, msi, kernel):

        lemma = kernel.lemma
        if not isinstance(lemma, unicode):
            lemma = unicode(lemma, "utf-8")

        if msi['category'] is "pronoun" and msi['type'] is "personal" and msi['person'] in [1, 2]:
            animity = AnimityEnum.animated

        elif msi['category'] is "pronoun" and msi['type'] is "personal" and msi['case'] is "dative":
            animity = AnimityEnum.animated

        elif msi['category'] is "pronoun" and msi['type'] is "personal" and msi['person'] is 3:
            animity = AnimityEnum.bianimate

        elif msi['category'] is "pronoun" and msi['type'] is "indefinite" and lemma in ["alguien", "nadie"]:
            animity = AnimityEnum.animated

        # check lemma against resources
        elif lemma in (self.persons + self.demonyms + self.animals) \
             or 'semantic_classification' in msi \
                and (msi['semantic_classification'] == 'person'
                     or msi['semantic_classification'] == 'organization'
                     or msi['semantic_classification'] == 'other'):

            animity = AnimityEnum.animated

        else:
            default_animity_value = AnimityEnum.inanimate
            animity = default_animity_value

        return animity

    def _get_items(self, config, resource):
        """
        load resource list of items

        :return: list of unicode words as list
        """
        items = []
        items_filename = config.get("resources", resource)

        for line in open(items_filename, 'r'):
            if line[0] not in ['<', '%', '\n']:
                item = (line.rstrip('\n')).rstrip('\r')
                if not isinstance(item, unicode):
                    item = unicode(item, 'utf-8')

                items.append(item)

        return items

    # Module Globals
    msi_seer_by_label = {"sn": msi_of_single,
                         "grup-nom-ms": msi_of_single,
                         "grup-nom-fs": msi_of_single,
                         "grup-nom-mp": msi_of_single,
                         "grup-nom-fp": msi_of_single,
                         "coor-n": msi_of_coordinated,
                         "patons": msi_of_leaf,
                         "ptonic": msi_of_leaf,
                         "grup-verb-inf": msi_of_infinity}
