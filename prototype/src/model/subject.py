# -*- coding: utf-8 -*-

from syntacticStructure import *

class Subject(SyntacticStructure):

    def __init__(self, lexical_form, msi):
        SyntacticStructure.__init__(self, "subject")
        self.lexical_form = lexical_form
        self.msi = msi

    def is_tacit(self):
        return not bool(self.entities)

    def __repr__(self):
        return ("(TACIT) " if self.is_tacit() else "") + self.lexical_form

    @staticmethod
    def concrete(entity):
        subject = Subject(str(entity), entity.msi)
        subject.entities = [ entity ]
        return subject

    @staticmethod
    def tacit(lexical_form, msi):
        return Subject(lexical_form, msi)
