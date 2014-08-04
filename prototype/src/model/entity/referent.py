# -*- coding: utf-8 -*-

class Referent:
    def __init__(self, entity):
        self.designated_ref = entity
        self.name = entity.lexical_form
        self.references = set([ entity ])

    def add_reference(self, entity):
        self.references.add(entity)

    def semantic_classification(self):
        msi = self.designated_ref.msi
        return msi["semantic_classification"] if "semantic_classification" in msi else None

    def ref_count(self):
        return len(self.references)

    def __repr__(self):
        return self.name + " [" + str(self.ref_count()) + "]"