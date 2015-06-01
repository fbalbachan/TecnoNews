# -*- coding: utf-8 -*-
from collections import deque
from traceback import format_exc

from src.ling.freelingDictionaryParser import FreelingDictionaryParser
from src.model.paragraph.paragraphAnalyzer import ParagraphAnalyzer
from src.model.paragraph.paragraph import Paragraph
from src.model.sentence.sentenceAnalyzer import SentenceAnalyzer
from src.rewrite.strategy.AppositionDislocationStrategy import AppositionDislocationStrategy
from src.rewrite.strategy.adverbialClauseDislocationStrategy import AdverbialClauseDislocationStrategy
from src.rewrite.strategy.althoughClauseDislocationStrategy import AlthoughClauseDislocationStrategy
from src.rewrite.strategy.dateTimeStrategy import DateTimeStrategy
from src.rewrite.strategy.futureToGoConstructionStrategy import FutureToGoConstructionStrategy
from src.rewrite.strategy.goConstructionToFutureStrategy import GoConstructionToFutureStrategy
from src.rewrite.strategy.modalDeberToTieneQue import ModalDeberToTieneQue
from src.rewrite.strategy.pastCompoundToSimpleStrategy import PastCompoundToSimpleStrategy
from src.rewrite.strategy.pastSimpleToCompoundStrategy import PastSimpleToCompoundStrategy
from src.rewrite.strategy.segunToDijoDislocationStrategy import SegunToDijoDislocationStrategy
from src.rewrite.strategy.subjunctiveImperfectStrategy import SubjunctiveImperfectStrategy
from src.rewrite.strategy.synonymsStrategy import SynonymsStrategy
from src.rewrite.strategy.tieneQueToModalDeber import TieneQueToModalDeber
from src.rewrite.strategy.textualCite import TextualCite
from src.rewrite.strategy.voicePassiveStrategy import VoicePassiveStrategy
from src.rewrite.strategy.partialVoicePassiveStrategy import PartialVoicePassiveStrategy


debug_mode = False


class Rewriter:
    def __init__(self, paragraph, ontology=None, strategies=None, clauses_for_replacements=None):
        if debug_mode: print "--> Rewriter.init()"

        if ontology is None:
            ontology = self.ontology

        if strategies is None:
            self.replacementStrategies = [SynonymsStrategy(ontology),
                                          PastSimpleToCompoundStrategy(ontology),
                                          PastCompoundToSimpleStrategy(ontology),
                                          ModalDeberToTieneQue(ontology),
                                          TieneQueToModalDeber(ontology),
                                          FutureToGoConstructionStrategy(ontology),
                                          GoConstructionToFutureStrategy(ontology),
                                          SubjunctiveImperfectStrategy(ontology)]

            self.dislocationStrategies = [AppositionDislocationStrategy(),
                                          VoicePassiveStrategy(ontology),
                                          PartialVoicePassiveStrategy(ontology),
                                          TextualCite(),
                                          AdverbialClauseDislocationStrategy(ontology),
                                          DateTimeStrategy(ontology),
                                          AlthoughClauseDislocationStrategy(),
                                          SegunToDijoDislocationStrategy()]
        else:
            self.replacementStrategies = []
            self.dislocationStrategies = []
            for strategy in strategies:
                if strategy.type == 'replacement':
                    self.replacementStrategies.append(strategy)
                else:
                    self.dislocationStrategies.append(strategy)

        self.paragraph = paragraph
        self.clauses_for_replacements = clauses_for_replacements

    def rewrite(self):
        if debug_mode: print "--> Rewriter.rewrite()"
        replacements = []

        clauses = self.clauses_for_replacements if self.clauses_for_replacements else self.paragraph.clauses()
        for clause in clauses:
            replacement_rules = self.replacements_for(clause)
            replacements.extend(replacement_rules)

        text = self.compose_text_with(replacements)
        for strategy in self.dislocationStrategies:
            self.paragraph = Paragraph.from_text(text)
            self.analyzer.analyze(self.paragraph)  # TODO: This seems to be called over and over (calling freeling)
            dislocations = self._dislocations_from(strategy, self.paragraph.sentences)
            text = self.compose_text_with(dislocations)
            if debug_mode: print "\nTEXT AFTER APPLYING STRATEGY: ", strategy.__class__.__name__, ":\n[", text, "]\n"

        return text

    def compose_text_with(self, rewrites):
        if debug_mode: print "--> Rewriter.compose_text_with(rewrites: ", rewrites, ")"
        rewrites.sort(key=lambda rewrite_rule: rewrite_rule.token().start())
        rewrites = deque(rewrites)

        source_text = self.paragraph.text.decode("utf-8")

        new_text = ""
        index = 0
        while rewrites:
            rewrite = rewrites.popleft()
            start, end = rewrite.token().start(), rewrite.token().end()
            new_text += source_text[index:start] + rewrite.replacement.decode("utf-8")
            index = end

        new_text += source_text[index:]

        if debug_mode: print "<-- compose_text_with() - source_text: ", new_text, "\n\n"
        return new_text.encode("utf-8")

    def _dislocations_from(self, strategy, sentences):
        if debug_mode: print "--> Rewriter._dislocations_from(strategy: ", strategy.__class__.__name__, ")"

        dislocations = []
        for sentence in sentences:
            try:
                dislocation_rewrite_rules = self._dislocations_from_node(strategy, sentence, sentence.parse_node)
                dislocations.extend(dislocation_rewrite_rules)

            except:
                pass  # TODO: Remove this exception handler when the problem is solved

        if debug_mode: print "<-- _dislocations_from() - dislocations: ", dislocations, "\n\n"
        return dislocations

        # TODO: Use the line below again after removing the handler above
        # return [strategy.rewrite(sentence) for sentence in sentences if strategy.applies_to(sentence)]

    def _dislocations_from_node(self, strategy, sentence, node):
        if debug_mode:
            strategy_name = strategy.__class__.__name__
            print "--> Rewriter._dislocations_from_node(strategy: ", strategy_name, ", node: ", node, ")"

        dislocations = []
        enter = True
        try:
            if strategy.applies_to(sentence, node):
                dislocation_rewrite_rule = strategy.rewrite(sentence, node)
                dislocations.append(dislocation_rewrite_rule)
                enter = False
        except:
            if debug_mode: print "\n\nException in _dislocations_from_node!!\n\n\n"
            pass

        if enter:
            for child in node.children:
                dislocation_rewrite_rules = self._dislocations_from_node(strategy, sentence, child)
                dislocations.extend(dislocation_rewrite_rules)

        return dislocations

    def replacements_for(self, clause):
        if debug_mode: print "--> Rewriter.replacements_for()"
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
            except:
                print format_exc()

        if debug_mode: print "<-- replacements_for() - replacements: ", replacements, "\n\n"
        return replacements

    def append_if_not_overlaps(self, rewrite, rewrites):
        if debug_mode: print "--> Rewriter.append_if_not_overlaps()"
        overlaps_rewrite_with_some_in_rewrites = any((each.overlaps(rewrite) for each in rewrites))
        if not overlaps_rewrite_with_some_in_rewrites:
            rewrites.append(rewrite)
        else:
            if debug_mode: print "Hay OVERLAP"

    sentenceAnalyzer = SentenceAnalyzer()
    analyzer = ParagraphAnalyzer(sentenceAnalyzer)

    ontology = FreelingDictionaryParser.from_resource()
    # ontology = Ontology("Test")
