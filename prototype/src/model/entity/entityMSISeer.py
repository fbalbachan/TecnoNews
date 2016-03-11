# -*- coding: utf-8 -*-
from src.ling.gender import Gender
from src.ling.number import Number

from src.model.entity.entitySemanticAnalyzer import EntitySemanticAnalyzer
from src.model.entity.animity import Animity
from src.utils.resources import instance as resources

debug_mode = False


class EntityMSISeer:

    def __init__(self):
        self.persons = resources.get_wordlist_safe("resources", "persons")
        self.demonyms = resources.get_wordlist_safe("resources", "demonyms")
        self.animals = resources.get_wordlist_safe("resources", "animals")

    def msi_of(self, entity):
        if debug_mode: print "--> EntityMSISeer.msi_of(entity:", entity, ")"

        label = entity.node.label
        entity.msi = self.msi_seer_by_label[label](self, entity) if label in self.msi_seer_by_label else {}
        semantic_analyzer = EntitySemanticAnalyzer()
        semantic_analyzer.analyze(entity)
        entity.msi["animity"] = self.calculate_animity_for(entity)
        return entity.msi

    def msi_of_single(self, entity):
        if debug_mode: print "--> EntityMSISeer.msi_of_single(entity:", entity, ")"

        useful_leaves = self.get_useful_leaves(entity)

        entity.kernel = useful_leaves.pop()

        msi = entity.kernel.msi

        if msi["category"] == "number":
            msi["gender"] = Gender.neutral
            msi["number"] = Number.invariable
            msi["type"] = "common"
            msi["category"] = "noun"

        if "person" not in msi or not msi["person"]:
            msi["person"] = 3

        if entity.kernel.msi["category"] == "determinant":
            msi["animity"] = Animity.bianimate
            msi["category"] = "noun"

        self.disambiguate_if_necessary(msi, useful_leaves)

        return msi

    def get_useful_leaves(self, entity):
        if debug_mode: print "--> EntityMSISeer.get_useful_leaves(entity:", entity, ")"
        node = entity.node

        banned_labels = ["grup-sp", "sp-de"]
        banned_nodes = filter(lambda child:
                                  not child.is_leaf() and child.label in banned_labels,
                              node.children)
        banned_nodes = set(banned_nodes)

        nouns = self.filter_banned(node.leaves_of_category("noun") + node.leaves_of_category("number"),
                                   banned_nodes)

        if self.has_unexchangeable_appositional_relationship(nouns):
            entity.attributes["class"] = [nouns[0].lexical_form]
            nouns = [nouns[1]]

        other_leaves = self.filter_banned(node.leaves_of_category("pronoun", "determinant", "adjective"),
                                          banned_nodes)

        useful_leaves = nouns + other_leaves

        useful_leaves.reverse()
        return useful_leaves

    def filter_banned(self, leaves, banned_nodes):
        return filter(lambda leaf: not banned_nodes & set(leaf.path_to_root()), leaves)

    def has_unexchangeable_appositional_relationship(self, kernel_nouns):
        return [noun.msi["type"] if "type" in noun.msi else None for noun in kernel_nouns] == ["common", "proper"]

    def disambiguate_if_necessary(self, msi, leaves):
        if debug_mode: print "--> EntityMSISeer.disambiguate_if_necessary(msi, leaves)", msi
        if not leaves:
            return
        leaves = leaves[::-1]

        non_neutral_attribute_values = {"gender": [Gender.masculine, Gender.feminine],
                                        "number": [Number.singular, Number.plural]}

        for attribute, non_neutral_values in non_neutral_attribute_values.items():
            if msi[attribute] not in non_neutral_values:
                for leaf in leaves:
                    if attribute in leaf.msi and leaf.msi[attribute] in non_neutral_values:
                        msi[attribute] = leaf.msi[attribute]

    def msi_of_coordinated(self, entity):
        msi = {"category": "noun", "number": Number.plural, "type": None, "semantic_classification": None}

        for a_child in entity.children:
            if a_child.classification() != None:
                msi["semantic_classification"] = a_child.classification()
                msi["type"] = a_child.msi["type"]
                break

        pronouns = sorted(entity.children_of_category("pronoun"), key=lambda pronoun: pronoun.person())
        msi["person"] = pronouns[0].person() if pronouns else 3

        genders = [child.gender()
                   for child in entity.children_of_category("noun") + entity.children_of_category("pronoun")]
        if Gender.masculine in genders:
            gender = Gender.masculine
        elif all(map(lambda p_gender: p_gender == Gender.feminine, genders)):
            gender = Gender.feminine
        else:
            gender = Gender.neutral

        msi["gender"] = gender

        return msi

    def msi_of_leaf(self, entity):
        msi = entity.node.leaves()[0].msi
        return msi

    def msi_of_infinity(self, entity):
        return {"category": "noun", "gender": None, "person": 3,
                "number": Number.singular, "type": None, "semantic_classification": None}

    def calculate_animity_for(self, entity):
        default_animity_value = Animity.inanimate

        # If entity has an animity value, other than the default, then return it (assuming it was previously calculated)
        if "animity" in entity.msi and entity.msi["animity"] is not default_animity_value:
            return entity.msi["animity"]

        elif len(entity.token.components) is 1 \
             and entity.msi['category'] == "pronoun" \
             and entity.msi['type'] == "indefinite" \
             and entity.node.lexical_form().lower() in ["ambos", "ambas"]:
            return Animity.bianimate

        # Entities with 1 token being a "paton" or "ptonic"
        elif len(entity.token.components) is 1 and entity.node.label in ["patons", "ptonic"]:
            if entity.msi['person'] in [1, 2]:
                return Animity.animated

            if entity.msi['person'] is 3 and entity.msi['case'] == "dative":
                return Animity.animated

            if entity.msi['person'] is 3:
                return Animity.bianimate

        elif entity.has_attr("implicit") or entity.node.label in ["grup-verb-inf"]:
            return Animity.inanimate

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
            animity = Animity.animated

        elif msi['category'] is "pronoun" and msi['type'] is "personal" and msi['case'] is "dative":
            animity = Animity.animated

        elif msi['category'] is "pronoun" and msi['type'] is "personal" and msi['person'] is 3:
            animity = Animity.bianimate

        elif msi['category'] is "pronoun" and msi['type'] is "indefinite" and lemma in ["alguien", "nadie"]:
            animity = Animity.animated

        # check lemma against resources
        elif lemma in (self.persons + self.demonyms + self.animals) \
             or 'semantic_classification' in msi \
                and (msi['semantic_classification'] == 'person'
                     or msi['semantic_classification'] == 'organization'
                     or msi['semantic_classification'] == 'other'):

            animity = Animity.animated

        else:
            default_animity_value = Animity.inanimate
            animity = default_animity_value

        return animity

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
