# -*- coding: utf-8 -*-
from collections import deque
from traceback import format_exc

from src.ling.freelingDictionaryParser import FreelingDictionaryParser
from src.model.paragraph.paragraph import Paragraph
from src.model.paragraph.paragraphAnalyzer import ParagraphAnalyzer
from src.model.sentence.sentenceAnalyzer import SentenceAnalyzer
from src.rewrite.strategy.adverbialClauseDislocationStrategy import AdverbialClauseDislocationStrategy
from src.rewrite.strategy.althoughClauseDislocationStrategy import AlthoughClauseDislocationStrategy
from src.rewrite.strategy.dateTimeStrategy import DateTimeStrategy
from src.rewrite.strategy.futureToGoConstructionStrategy import FutureToGoConstructionStrategy
from src.rewrite.strategy.goConstructionToFutureStrategy import GoConstructionToFutureStrategy
from src.rewrite.strategy.modalDeberToTieneQue import ModalDeberToTieneQue
from src.rewrite.strategy.pastCompoundToSimpleStrategy import PastCompoundToSimpleStrategy
from src.rewrite.strategy.pastSimpleToCompoundStrategy import PastSimpleToCompoundStrategy
from src.rewrite.strategy.segunToDijoDislocationStrategy import SegunToDijoDislocationStrategy
from src.rewrite.strategy.subjuntiveImperfectStrategy import SubjuntiveImperfectStrategy
from src.rewrite.strategy.synonymsStrategy import SynonymsStrategy
from src.rewrite.strategy.tieneQueToModalDeber import TieneQueToModalDeber
from src.rewrite.strategy.textualCite import TextualCite


class Rewriter:
    def __init__(self, paragraph, ontology = None, strategies = None, clausesForReplacements = None):
        if ontology == None:
            ontology = self.ontology

        if strategies == None:
            self.replacementStrategies = [
                SynonymsStrategy(ontology),
                PastSimpleToCompoundStrategy(ontology),
                PastCompoundToSimpleStrategy(ontology),

                SubjuntiveImperfectStrategy(ontology),

                FutureToGoConstructionStrategy(ontology),
                GoConstructionToFutureStrategy(ontology),

                ModalDeberToTieneQue(ontology),
                TieneQueToModalDeber(ontology)

            ]
            self.dislocationStrategies = [
                AdverbialClauseDislocationStrategy(ontology),
                AlthoughClauseDislocationStrategy(),
                DateTimeStrategy(ontology),
                SegunToDijoDislocationStrategy(),
                TextualCite()
            ]
        else:
            self.replacementStrategies = []
            self.dislocationStrategies = []
            for strategy in strategies:
                if strategy.type == 'replacement': self.replacementStrategies.append(strategy)
                else: self.dislocationStrategies.append(strategy)

        self.paragraph = paragraph
        self.clausesForReplacements = clausesForReplacements

    def rewrite(self):
        replacements = []
        clauses = self.paragraph.clauses() if not self.clausesForReplacements else self.clausesForReplacements
        for clause in clauses:
            replacements.extend(self.replacements_for(clause))


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

    def dislocations_from_node(self, strategy, sentence, node):
        dislocations = []
        enter = True
        try:
            if strategy.applies_to(sentence, node):
                dislocations.append(strategy.rewrite(sentence, node))
                enter = False
        except: pass
        if enter:
            for child in node.children:
                dislocations.extend(self.dislocations_from_node(strategy, sentence, child))
        return dislocations

    def dislocations_from(self, strategy):
        # TODO: Remove this exception handler when the problem is solved
        dislocations = []
        for sentence in self.paragraph.sentences:
            try:
                dislocations.extend(self.dislocations_from_node(strategy, sentence, sentence.parse_node))
            except:
                pass
        return dislocations
        # TODO: Use the line below again after removing the handler above
        #return [ strategy.rewrite(sentence) for sentence in self.paragraph.sentences if strategy.applies_to(sentence) ]

    def replacements_for(self, clause):
        replacements = []
        for strategy in self.replacementStrategies:
            try:
                if strategy.applies_to(clause):
                    rewrites = strategy.rewrite(clause)
                    if type(rewrites) == list:
                        for rewrite in rewrites:
                            self.append_if_not_overlaps(rewrite, replacements)
                    else:
                        self.append_if_not_overlaps(rewrites, replacements)
            except: print format_exc()
        return replacements

    def append_if_not_overlaps(self, rewrite, rewrites):
        if not any(( each.overlaps(rewrite) for each in rewrites )):
            rewrites.append(rewrite)
        else:
            print "Hay OVERLAP"

    sentenceAnalyzer = SentenceAnalyzer()
    analyzer = ParagraphAnalyzer(sentenceAnalyzer)

    ontology = FreelingDictionaryParser.from_resource()
    #ontology = Ontology("Test")
