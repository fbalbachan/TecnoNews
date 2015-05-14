# -*- coding: utf-8 -*-
from src.model.referent.referent import Referent
from src.sentiment.entitySentimentalValue import EntitySentimentalValue
from src.model.entity.animityEnum import AnimityEnum


class TacitEntity:
    def __init__(self, lexical_form, msi, attributes=None):
        self.lexical_form = lexical_form
        if 'animity' not in msi:
            msi["animity"] = AnimityEnum.inanimate
        self.msi = msi
        self.children = []
        self.owner = None

        if not attributes:
            attributes = {"tacit": None}
        self.attributes = attributes
        self.sentimental_value = EntitySentimentalValue(self)
        self.coref_chain = []
        self.referent = Referent(self)

    def contains(self, other):
        is_contained = other in self.children
        return is_contained

    def referenced(self):
        return self.coref_chain[-1]

    def add_coreference(self, referenced):
        if referenced.is_linked():
            self.coref_chain.extend(referenced.coref_chain)
        else:
            self.coref_chain.append(referenced)

        self.update_referent(self.referenced().referent)
        self.update_msi()

    def update_msi(self):
        msi = self.msi
        referenced_msi = self.referenced().msi
        if msi["gender"] == "neutral":
            msi["gender"] = referenced_msi["gender"]
        msi["animity"] = referenced_msi["animity"]

    def update_referent(self, referent):
        self.referent = referent
        referent.add_reference(self)

    def words(self):
        return self.lexical_form.split("_")

    def children_of_category(self, category):
        return filter(lambda entity: entity.category() == category, self.children)

    #
    # Methods related to MSI (morfo-syntatic-information)
    #
    def classification(self):
        return self.msi["semantic_classification"]

    def category(self):
        return self.msi["category"]

    def matches(self, entity):
        matches = self.msi["person"] == entity.msi["person"] \
                  and self.matches_number_of(entity) \
                  and self.matches_gender_of(entity)
        return matches

    def number_matches(self, number):
        msi = self.msi
        return msi["number"] == "invariable" \
               or number == "invariable" \
               or msi["number"] == number

    def matches_number_of(self, entity):
        return self.number_matches(entity.msi["number"])

    def gender_matches(self, gender):
        neutral_genders = ["neutral", "common"]
        return self.msi["gender"] in neutral_genders \
               or gender in neutral_genders \
               or self.msi["gender"] == gender

    def matches_gender_of(self, entity):
        return self.gender_matches(entity.msi["gender"])

    def matches_msi(self, msi):
        for key, value in msi.items():
            if key not in self.msi:
                return False

            if self.msi[key] != value:      #TODO: add here specialized comparisons instead of "=="
                return False                #      such as matches_gender_of, matches_number_of, etc
        return True

    def animity_matches(self, animity):
        return AnimityEnum.animities_match(self.msi["animity"], animity)

    def matches_animity_of(self, entity):
        return AnimityEnum.animities_match(self.msi["animity"], entity.msi["animity"])

    #
    # Methods to classify th entity
    #
    def is_linked(self):
        return bool(self.coref_chain)

    def is_tacit(self):
        return self.has_attr("tacit")

    def is_implicit(self):
        return self.has_attr("implicit")

    def is_impersonal(self):
        return self.has_attr("impersonal")

    def is_explicit(self):
        explicit = not self.is_implicit() and \
                   not self.is_tacit() and \
                   not self.is_impersonal()
        return explicit

    def is_trace(self):
        return self.is_implicit() or self.is_impersonal()

    def is_coordinated(self):
        return self.has_attr("coordinated")

    def has_attr(self, attribute):
        return attribute in self.attributes

    def is_possessed(self):
        return bool(self.owner)

    def __repr__(self):
        flag = "(implicit)" if self.has_attr("implicit") else "(impersonal)" if self.has_attr("impersonal") else "(tacit)"
        _repr = flag + " " + self.lexical_form
        if self.is_linked():
            _repr = _repr + " (" + self.referenced().lexical_form + ")"
        return _repr

    def name(self):
        return repr(self)
