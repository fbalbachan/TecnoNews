# -*- coding: utf-8 -*-
from src.ling.gender import Gender
from src.ling.number import Number
from src.model.referent.referent import Referent
from src.sentiment.entitySentimentalValue import EntitySentimentalValue
from src.model.entity.animity import Animity

debug_mode = False


class TacitEntity:
    def __init__(self, lexical_form, msi, attributes=None):
        if debug_mode: print "--> TacitEntity.init(lexical_form:", lexical_form, ")"
        self.lexical_form = lexical_form
        if 'animity' not in msi:
            msi["animity"] = Animity.inanimate
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
        return self.referenced().referent.designated_ref() if self.is_linked() else self.referent.designated_ref()

    def add_coreference(self, referenced):
        if referenced.is_linked():
            self.coref_chain.extend(referenced.coref_chain)
        else:
            self.coref_chain.append(referenced)

        self.update_referent(self.referenced().referent)
        self.update_msi()

    def update_msi(self):
        referenced = self.referenced()
        if self.gender() == Gender.neutral:
            self.msi["gender"] = referenced.gender()

        self.msi["animity"] = referenced.msi["animity"]

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
    def classification(self, is_deep_classification=False):
        entity = self.referenced_entity() if is_deep_classification else self
        if entity.category() == "noun" \
           and entity.msi["type"] == "proper" \
           and "semantic_classification" in entity.msi:
            return entity.msi["semantic_classification"]
        else:
            return None

    def category(self):
        return self.msi["category"]

    def number(self):
        return self.msi["number"]

    def gender(self):
        return self.msi["gender"]

    def person(self):
        return self.msi["person"]

    def matches(self, entity):
        print "M self: ", self, " - entity: ", entity
        matches = self.person() == entity.person() \
                  and self.number_matches(entity.number()) \
                  and self.gender_matches(entity.gender())
        return matches

    def number_matches(self, number):
        return self.number() == Number.invariable \
               or number == Number.invariable \
               or self.number() == number

    def gender_matches(self, gender):
        return self.gender() == Gender.neutral \
               or gender == Gender.neutral \
               or self.gender() == gender

    def animity_matches(self, animity):
        return Animity.animities_match(self.msi["animity"], animity)

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

    def matches_animity_of(self, entity):
        return Animity.animities_match(self.msi["animity"], entity.msi["animity"])

    def matches_number_of(self, entity):
        return Number.numbers_match(self.number(), entity.number())

    def matches_gender_of(self, entity):
        return Gender.genders_match(self.gender(), entity.gender())

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

    def has_many_referents(self):
        return len(self.referent.references) > 1

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
            _repr = _repr + " (referent: " + self.referenced().lexical_form + ")"
        return _repr

    def name(self):
        return repr(self)

    def real_name(self):
        return self.referenced().referent.name() if self.is_linked() else self.referent.name()