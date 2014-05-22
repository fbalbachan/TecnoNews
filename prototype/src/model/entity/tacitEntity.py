# -*- coding: utf-8 -*-


class TacitEntity:

    def __init__(self, lexical_form, msi):
        self.lexical_form = lexical_form
        self.msi = msi
        self.children = []
        self.owner = None

    def children_of_category(self, category):
        return filter(lambda entity: entity.category() == category, self.children)

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
        return False

    def is_tacit(self):
        return True

    def is_possessed(self):
        return bool(self.owner)

    def __repr__(self):
        return "(tacit) " + self.lexical_form