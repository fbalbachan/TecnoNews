# -*- coding: utf-8 -*-
from src.model.referent.referent import Referent
from src.sentiment.entitySentimentalValue import EntitySentimentalValue
from src.model.entity.animity import Animity


class TacitEntity:

    # Cuidado! El diccionario attributes se instancia siempre con una referencia al mismo diccionario default!
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

    def matches_number_of(self, entity):
        msi = self.msi
        return msi["number"] == "invariable" \
               or entity.msi["number"] == "invariable" \
               or msi["number"] == entity.msi["number"]

    def matches_gender_of(self, entity):
        neutral_genders = ["neutral", "common"]
        msi = self.msi
        return msi["gender"] in neutral_genders \
               or entity.msi["gender"] in neutral_genders \
               or msi["gender"] == entity.msi["gender"]

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
