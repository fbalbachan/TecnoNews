# -*- coding: utf-8 -*-
from src.sentiment.sentiWordNet import SentiWordNet
from src.sentiment.sentimentalValuedObject import SentimentalValuedObject


class SentimentalAnalyzer:
    def analyze(self, clause):
        for entity in clause.entities:
            self.analyze_entity(entity)

    def analyze_entity(self, entity):
        if not entity.is_tacit():
            for method in [ self.analyze_adjectival, self.analyze_nominal ]: method(entity)

    def analyze_adjectival(self, entity):
        node = entity.proper_node
        hints = node.leaves_of_category("adjective") + node.leaves_of_msi({ "category": "verb", "mode" : "participio"})
        evidence = self.only_valuated_of(hints)
        entity.sentimental_value.add_evidence(*evidence)

    def analyze_nominal(self, entity):
        node = entity.proper_node
        hints = node.leaves_of_category("noun") + node.leaves_of_msi({ "category": "verb", "mode" : "infinitive"})
        evidence = self.only_valuated_of(hints)
        entity_value = entity.sentimental_value
        entity_value.add_evidence(*evidence)
        if entity.father: entity.father.sentimental_value.add_evidence(entity_value)

    def only_valuated_of(self, hints):
        valuated = []
        for hint in hints:
            word_value = SentiWordNet.get(hint.lemma)
            if not word_value.is_neutral(): valuated.append(SentimentalValuedObject(hint, word_value.value))
        return valuated