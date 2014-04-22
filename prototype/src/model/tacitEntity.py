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
        msi = self.msi
        return msi["gender"] == "neutral" or entity.msi["gender"] == "neutral" or msi["gender"] == entity.msi["gender"]

    def __repr__(self):
        return "(tacit) " + self.lexical_form