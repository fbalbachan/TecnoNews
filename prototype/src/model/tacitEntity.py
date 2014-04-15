# -*- coding: utf-8 -*-

class TacitEntity:

    def __init__(self, lexical_form, msi):
        self.lexical_form = lexical_form
        self.msi = msi

    def __repr__(self):
        return "(tacit) " + self.lexical_form