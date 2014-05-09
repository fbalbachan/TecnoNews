# -*- coding: utf-8 -*-

class SyntacticStructure:
    def __init__(self, name):
        self.name = name
        self.entities = []
        self.tacit_entities = []

    def replace(self, old_entity, new_entity):
        self.remove(old_entity)
        self.append(new_entity)

    def remove(self, entity):
        for entity_list in [ self.entities, self.tacit_entities ]:
            if entity in entity_list:
                entity_list.remove(entity)
                break

    def append(self, entity):
        entity_list = self.tacit_entities if entity.is_tacit() else self.entities
        entity_list.append(entity)

    def category(self):
        return self.msi()["category"]

    def msi(self):
        return self.entity().msi

    def lexical_form(self):
        return self.entity().lexical_form

    def is_empty(self):
        return not bool(self.all_entities())

    def all_entities(self):
        return self.entities + self.tacit_entities

    def entity(self):
        return self.all_entities()[0]

    def is_tacit(self):
        return not bool(self.entities) and bool(self.tacit_entities)

    def __repr__(self):
        entities = self.entities + self.tacit_entities
        return str(entities[0] if len(entities) == 1 else entities)