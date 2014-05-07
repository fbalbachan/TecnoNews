# -*- coding: utf-8 -*-
from src.model.tacitEntity import TacitEntity

class LinkedEntity(TacitEntity):
    def __init__(self, entity, referenced_entity):
        TacitEntity.__init__(self, referenced_entity.lexical_form, referenced_entity.msi)
        self.entity = entity
        self.referenced_entity = referenced_entity

    def contains(self, other):
        return self.entity.contains(other)

    def __repr__(self):
        return self.entity.lexical_form + " (" + self.lexical_form + ")"