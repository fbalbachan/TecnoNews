# -*- coding: utf-8 -*-
from src.model.referent.referent import Referent
from src.sentiment.entitySentimentalValue import EntitySentimentalValue


class TacitEntity:

    def __init__(self, lexical_form, msi, attributes = { "tacit" : None }):
        self.lexical_form = lexical_form
        self.msi = msi
        self.children = []
        self.owner = None
        self.attributes = attributes
        self.sentimental_value = EntitySentimentalValue(self)
        self.coref_chain = []
        self.referent = Referent(self)

    def referenced(self):
        return self.coref_chain[-1]

    def add_coreference(self, referenced):
        if not referenced.is_linked():
            self.coref_chain.append(referenced)
        else:
            self.coref_chain.extend(referenced.coref_chain)

        self.update_referent(self.referenced().referent)

    def update_referent(self, referent):
        self.referent = referent
        referent.add_reference(self)

    def words(self):
        return self.lexical_form.split("_")

    def children_of_category(self, category):
        return filter(lambda entity: entity.category() == category, self.children)

    def classification(self):
        return self.msi["semantic_classification"]

    def category(self):
        return self.msi["category"]

    def matches(self, entity):
        matches = self.msi["person"] == entity.msi["person"] \
            and self.matches_number_of(entity) and self.matches_gender_of(entity)
        return matches

    def matches_number_of(self, entity):
        msi = self.msi
        return msi["number"] == "invariable" or entity.msi["number"] == "invariable" \
            or msi["number"] == entity.msi["number"]

    def matches_gender_of(self, entity):
        neutral_genders = [ "neutral", "common" ]
        msi = self.msi
        return msi["gender"] in neutral_genders or entity.msi["gender"] in neutral_genders \
            or msi["gender"] == entity.msi["gender"]

    def is_linked(self):
        return bool(self.coref_chain)

    def is_tacit(self):
        return self.has_attr("tacit")

    def is_coordinated(self):
        return self.has_attr("coordinated")

    def has_attr(self, attribute):
        return attribute in self.attributes

    def is_possessed(self):
        return bool(self.owner)

    def __repr__(self):
        _repr = "(tacit) " + self.lexical_form
        if self.is_linked(): _repr = _repr + " (" + self.referenced().lexical_form + ")"
        return _repr

    def name(self):
        return repr(self)
