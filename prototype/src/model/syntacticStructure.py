# -*- coding: utf-8 -*-

class SyntacticStructure:
    def __init__(self, name):
        self.name = name
        self.entities = []
        self.tacit_entities = []

    def replace(self, old_entity, new_entity):
        for entity_list in [ self.entities, self.tacit_entities ]:
            if old_entity in entity_list:
                entity_list.remove(old_entity)
                entity_list.append(new_entity)
                break

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