# -*- coding: utf-8 -*-

class EntitySentimentalValue:
    def __init__(self, entity):
        self.entity = entity
        self.evidence = []
        self.value = (0, 0)

    def object(self):
        return self.entity

    def add_evidence(self, *evidence):
        self.evidence.extend(evidence)
        if self.evidence: self.compute_value()

    def compute_value(self):
        arrenged = zip(*[ each.value for each in self.evidence ])
        self.value = (sum(arrenged[0]), sum(arrenged[1]))

    def positive_evidence(self):
        return filter(lambda evidence: evidence.value[0], self.evidence)

    def negative_evidence(self):
        return filter(lambda evidence: evidence.value[1], self.evidence)

    def __repr__(self):
        return str(self.entity) + " " + str(self.value) + " " + str(self.evidence)