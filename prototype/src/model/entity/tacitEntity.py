# -*- coding: utf-8 -*-
from src.model.referent.referent import Referent
from src.sentiment.entitySentimentalValue import EntitySentimentalValue
from src.model.entity.animity import Animity
from collections import deque

class TacitEntity:

    # Warning! The dictionary of attributes is always instantiated with a reference to the same default dictionary!
    def __init__(self, lexical_form, msi, attributes={"tacit": None}):

        self.lexical_form = lexical_form
        if 'animity' not in msi:
            msi["animity"] = Animity.inanimate
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
            if not key in self.msi:
                return False

            if self.msi[key] != value:      #TODO: add here specialized comparisons instead of "=="
                return False                #      such as matches_gender_of, matches_number_of, etc
        return True

    def animity_matches(self, animity):
        return Animity.animities_match(self.msi["animity"], animity)

    def matches_animity_of(self, entity):
        return Animity.animities_match(self.msi["animity"], entity.msi["animity"])

    def is_linked(self):
        return bool(self.coref_chain)

    def is_tacit(self):
        return self.has_attr("tacit")

    def is_coordinated(self):
        return self.has_attr("coordinated")

    def get_nested_entities(self, include_myself=False):
        nested_entities = []
        q = deque()

        if include_myself:
            nested_entities.append(self)

        q.extend(self.children)
        while len(q) > 0:
            next_entity = q.popleft()
            nested_entities.append(next_entity)
            q.extend(next_entity.children)

        return nested_entities

    def has_attr(self, attribute):
        return attribute in self.attributes

    def is_possessed(self):
        return bool(self.owner)

    def __repr__(self):
        _repr = ("(implicit)" if self.has_attr("implicit") else "(tacit)") + " " + self.lexical_form
        if self.is_linked(): _repr = _repr + " (" + self.referenced().lexical_form + ")"
        return _repr

    def name(self):
        return repr(self)
