# -*- coding: utf-8 -*-

class TacitEntity:

    def __init__(self, lexical_form, msi):
        self.lexical_form = lexical_form
        self.msi = msi

    def category(self):
        return self.msi["category"]

    def matches(self, entity):
        matches = self.msi["number"] == entity.msi["number"] and self.msi["person"] == entity.msi["person"] and \
            self.matches_gender_of(entity)
        return matches

    def matches_gender_of(self, entity):
        neutral_genders = [ "neutral", "common" ]
        msi = self.msi
        return msi["gender"] in neutral_genders or entity.msi["gender"] in neutral_genders \
            or msi["gender"] == entity.msi["gender"]

    def is_linked(self):
        return False

    def is_tacit(self):
        return True

    def __repr__(self):
        return "(tacit) " + self.lexical_form