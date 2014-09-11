# -*- coding: utf-8 -*-
from collections import deque

from src.ling.freelingDictionaryParser import FreelingDictionaryParser
from src.rewrite.strategy.futureToGoConstructionStrategy import FutureToGoConstructionStrategy
from src.rewrite.strategy.pastSimpleToCompoundStrategy import PastSimpleToCompoundStrategy
from src.rewrite.strategy.subjuntiveImperfectStrategy import SubjuntiveImperfectStrategy
from src.rewrite.strategy.verbalSynStrategy import VerbalSynStrategy


class Rewriter:
    def __init__(self, paragraph):
        self.paragraph = paragraph

    def rewrite(self):
        rewrites = []
        for clause in self.paragraph.clauses():
                rewrites.extend(self.rewrites_for(clause))

        #print rewrites

        return self.compose_text_with(rewrites)

    def compose_text_with(self, rewrites):
        rewrites.sort(key = lambda rewrite: rewrite.token().start())
        rewrites = deque(rewrites)

        text = self.paragraph.text.decode("utf-8")

        source_text = ""
        index = 0

        while rewrites:
            rewrite = rewrites.popleft()

            start, end = rewrite.token().start(), rewrite.token().end()
            source_text += text[index:start] + rewrite.replacement.decode("utf-8")
            index = end

        source_text += text[index:]
        return source_text.encode("utf-8")

    def rewrites_for(self, clause):
        return [ strategy.rewrite(clause) for strategy in self.strategies if strategy.applies_to(clause) ]

    ontology = FreelingDictionaryParser.from_resource()
    strategies = [PastSimpleToCompoundStrategy(ontology), SubjuntiveImperfectStrategy(ontology),\
                  FutureToGoConstructionStrategy(ontology) ]