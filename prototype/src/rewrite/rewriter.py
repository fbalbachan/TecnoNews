# -*- coding: utf-8 -*-
from collections import deque

from src.ling.freelingDictionaryParser import FreelingDictionaryParser
from src.model.paragraph.paragraph import Paragraph
from src.model.paragraph.paragraphAnalyzer import ParagraphAnalyzer
from src.model.sentence.sentenceAnalyzer import SentenceAnalyzer
from src.rewrite.strategy.adverbialClauseDislocationStrategy import AdverbialClauseDislocationStrategy
from src.rewrite.strategy.futureToGoConstructionStrategy import FutureToGoConstructionStrategy
from src.rewrite.strategy.pastSimpleToCompoundStrategy import PastSimpleToCompoundStrategy
from src.rewrite.strategy.subjuntiveImperfectStrategy import SubjuntiveImperfectStrategy
from tests.freelingTreeRepository import FreelingTreeRepository


class Rewriter:
    def __init__(self, paragraph, ontology = None, strategies = None):
        if ontology == None:
            ontology = self.ontology

        if strategies == None:
            self.replacementStrategies = [
                PastSimpleToCompoundStrategy(ontology),
                SubjuntiveImperfectStrategy(ontology),
                FutureToGoConstructionStrategy(ontology)
            ]
            self.dislocationStrategies = [
                AdverbialClauseDislocationStrategy()
            ]
        else:
            self.replacementStrategies = []
            self.dislocationStrategies = []
            for strategy in strategies:
                if strategy.type == 'replacement': self.replacementStrategies.append(strategy)
                else: self.dislocationStrategies.append(strategy)

        self.paragraph = paragraph

    def rewrite(self):
        replacements = []
        for clause in self.paragraph.clauses():
            replacements.extend(self.replacements_for(clause))

        #print rewrites

        text = self.compose_text_with(replacements)
        for strategy in self.dislocationStrategies:

            self.paragraph = Paragraph.from_text(text)
            self.analyzer.analyze(self.paragraph) # TODO: Check if this is needed

            dislocations = self.dislocations_from(strategy)
            text = self.compose_text_with(dislocations)

        return text

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

    def dislocations_from(self, strategy):
        # TODO: Remove this exception handler when the problem is solved
        dislocations = []
        for sentence in self.paragraph.sentences:
            try:
                if strategy.applies_to(sentence):
                    dislocations.append(strategy.rewrite(sentence))
            except:
                pass
        return dislocations
        # TODO: Use the line below again after removing the handler above
        #return [ strategy.rewrite(sentence) for sentence in self.paragraph.sentences if strategy.applies_to(sentence) ]

    def replacements_for(self, clause):
        replacements = []
        for strategy in self.replacementStrategies:
            try:
                if strategy.applies_to(clause): replacements.append(strategy.rewrite(clause))
            except: pass
        return replacements

    sentenceAnalyzer = SentenceAnalyzer(FreelingTreeRepository("tests/input/trees"))
    analyzer = ParagraphAnalyzer(sentenceAnalyzer)
    ontology = FreelingDictionaryParser.from_resource()

