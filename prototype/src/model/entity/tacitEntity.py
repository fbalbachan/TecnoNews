# -*- coding: utf-8 -*-
from src.ling.genderEnum import GenderEnum
from src.ling.numberEnum import NumberEnum
from src.model.referent.referent import Referent
from src.sentiment.entitySentimentalValue import EntitySentimentalValue
from src.model.entity.animityEnum import AnimityEnum

debug_mode = False


class TacitEntity:
    def __init__(self, lexical_form, msi, attributes=None):
        if debug_mode: print "--> TacitEntity.init(lexical_form:", lexical_form, ")"
        self.lexical_form = lexical_form
        if 'animity' not in msi:
            msi["animity"] = AnimityEnum.inanimate
        self.msi = msi
        self.children = []
        self.owner = None

        if attributes is None:
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

    def referenced_entity(self):
        if self.is_linked():
            referenced_entity = self.referenced()
            if "referent" in dir(referenced_entity) and referenced_entity.referent is not None:
                referenced_entity = referenced_entity.referent.designated_ref()

        elif "referent" in dir(self) and self.referent is not None:
            referenced_entity = self.referent.designated_ref()

        else:
            referenced_entity = self

        return referenced_entity

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
        if msi["gender"] == GenderEnum.neutral:
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
    def classification(self, is_light_classification=True):
        entity = self if is_light_classification else self.referenced_entity()
        if entity.category() == "noun" \
           and entity.msi["type"] == "proper" \
           and "semantic_classification" in entity.msi:
            return entity.msi["semantic_classification"]
        else:
            return None

    def category(self):
        return self.msi["category"]

    def matches(self, entity):
        matches = self.msi["person"] == entity.msi["person"] \
                  and self.number_matches(entity.msi["number"]) \
                  and self.gender_matches(entity.msi["gender"])
        return matches

    def number_matches(self, number):
        msi = self.msi
        return msi["number"] == NumberEnum.invariable \
               or number == NumberEnum.invariable \
               or msi["number"] == number

    def gender_matches(self, gender):
        return self.msi["gender"] == GenderEnum.neutral \
               or gender == GenderEnum.neutral \
               or self.msi["gender"] == gender

    def matches_msi(self, msi):
        for key, value in msi.items():
            if key not in self.msi:
                return False

            if key == "gender" and not self.gender_matches(value) \
               or key == "number" and not self.number_matches(value) \
               or key == "animity" and not self.animity_matches(value):
                return False

            if self.msi[key] != value:
                return False
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

    def is_useless(self):
        return self.has_attr("useless")

    def is_explicit(self):
        explicit = not self.is_implicit() and \
                   not self.is_tacit() and \
                   not self.is_impersonal()
        return explicit

    def is_trace(self):
        return self.is_implicit() \
            or self.is_impersonal() \
            or self.is_useless()

    def is_coordinated(self):
        return self.has_attr("coordinated")

    def has_attr(self, attribute):
        return attribute in self.attributes

    def is_possessed(self):
        return bool(self.owner)

    def is_maximal_regarding(self, entities):
        is_maximal = not any([other.contains(self) for other in entities])
        return is_maximal

    def is_named_entity(self):
        return self.category() == "noun" and self.msi["type"] == "proper"\
               and self.classification() is not None

    def __repr__(self):
        flag = "(implicit)" if self.has_attr("implicit") \
                else "(impersonal)" if self.has_attr("impersonal") \
                else "(tacit)"
        _repr = flag + " " + self.lexical_form
        if self.is_linked():
            _repr = _repr + " (" + self.referenced().lexical_form + ")"
        return _repr

    def name(self):
        return repr(self)

    def real_name(self):
        if self.is_linked():
            real_name = self.referenced().lexical_form
            referent_entity = self.referenced()

            if "referent" in dir(referent_entity) and referent_entity.referent is not None:
                real_name = referent_entity.referent.name()
                referent_entity = referent_entity.referent.designated_ref()

        elif "referent" in dir(self) and self.referent is not None:
            real_name = self.referent.name()
            referent_entity = self.referent.designated_ref()

        else:
            referent_entity = self
            real_name = referent_entity.lexical_form

        return real_name