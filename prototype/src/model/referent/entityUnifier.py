# -*- coding: utf-8 -*-
from src.model.entity.entityMatchingAnalyzer import EntityMatchingAnalyzer

class EntityUnifier:
    def __init__(self, paragraph):
        self.paragraph = paragraph

    def unify(self):
        entities = list(self.paragraph.entities())
        while len(entities) > 1:
            source = entities.pop()
            matching_analyzer = EntityMatchingAnalyzer(source)

            for other in entities:
                if matching_analyzer.matches(other): other.update_referent(source.referent)
