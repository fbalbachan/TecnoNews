# -*- coding: utf-8 -*-
from src.model.entity.entityMatchingAnalyzer import EntityMatchingAnalyzer

class EntityUnifier:
    def __init__(self, paragraph):
        self.paragraph = paragraph

    def unify(self):
        entities = list(self.paragraph.entities())

        while len(entities) > 1:
            source = entities.pop()
            if source.is_linked(): continue

            matching_analyzer = EntityMatchingAnalyzer(source)

            for other in ( entity for entity in entities if not entity.is_linked() ):
                if matching_analyzer.matches(other):
                    self.update_referent(source, other)

    def update_referent(self, source, other):
        for reference in other.referent.references:
            reference.update_referent(source.referent)

