# -*- coding: utf-8 -*-
from src.model.tacitEntity import TacitEntity

class LinkedEntity(TacitEntity):
    def __init__(self, source, referenced_entity):
        TacitEntity.__init__(self, referenced_entity.lexical_form, referenced_entity.msi)
        self.source = source
        self.referenced_entity = referenced_entity

    def contains(self, other):
        return self.source.contains(other)

    def is_linked(self):
        return True

    def __repr__(self):
        return self.source.lexical_form + " (" + self.lexical_form + ")"