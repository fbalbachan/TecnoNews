# -*- coding: utf-8 -*-
from src.sentiment.sentimentalValuedObject import SentimentalValuedObject

class EntitySentimentalValue(SentimentalValuedObject):
    def __init__(self, entity):
        SentimentalValuedObject.__init__(self, entity)

    def evidence(self):
        return self.children

    def add_evidence(self, *evidence):
        self.children.extend(evidence)
        if self.evidence():
            self.compute_value()

    def compute_value(self):
        arrenged = list(zip(*[ each.value for each in self.evidence() ]))
        self.value = (sum(arrenged[0]), sum(arrenged[1]))

    def positive_evidence(self):
        return [evidence for evidence in self.evidence() if evidence.value[0]]

    def negative_evidence(self):
        return [evidence for evidence in self.evidence() if evidence.value[1]]

    def __repr__(self):
        return SentimentalValuedObject.__repr__(self) + " " + str(self.evidence())
