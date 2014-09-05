# -*- coding: utf-8 -*-
from src.rewrite.strategy.verbalSynStrategy import VerbalSynStrategy

class Rewriter:
    def __init__(self, paragraph):
        self.paragraph = paragraph

    def rewrite(self):
        rewrites = []
        for clause in self.paragraph.clauses():
                rewrites.extend(self.rewrites_for(clause))

        print rewrites

        return self.compose_text_with(rewrites)

    def compose_text_with(self, rewrites):
        rewrites.sort(key = lambda rewrite: rewrite.token().start())

    def rewrites_for(self, clause):
        return [ strategy.rewrite(clause) for strategy in self.strategies if strategy.applies_to(clause) ]

    strategies = [ VerbalSynStrategy() ]