# -*- coding: utf-8 -*-
from src.model.entity.entity import Entity
from src.model.entity.tacitEntity import TacitEntity


class LinkedEntity(Entity):
    def __init__(self, source, referenced_entity):
        Entity.__init__(self, referenced_entity.node)
        TacitEntity.__init__(self, referenced_entity.lexical_form, self.enriched_msi(source, referenced_entity))

        self.source = source
        self.referenced_entity = referenced_entity

    def enriched_msi(self, source, referenced_entity):
        source_msi = source.msi
        msi = referenced_entity.msi.copy()
        if msi["gender"] == "neutral": msi["gender"] = source_msi["gender"]
        if msi["number"] == "invariable": msi["number"] = source_msi["number"]
        return msi

    def contains(self, other):
        return self.source.contains(other)

    def is_linked(self):
        return True

    def is_tacit(self):
        return False

    def __repr__(self):
        return self.source.lexical_form + " (" + self.lexical_form + ")"