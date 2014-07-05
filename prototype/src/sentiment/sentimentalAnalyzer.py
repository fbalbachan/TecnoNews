# -*- coding: utf-8 -*-
from src.model.go.globalOperator import GlobalOperator
from src.sentiment.isolatedAdjectiveAnalyzer import IsolatedAdjectiveAnalyzer
from src.sentiment.sentiWordNet import SentiWordNet
from src.sentiment.sentimentalValuedObject import SentimentalValuedObject
from src.sentiment.verbalSentimentAnalyzer import VerbalSentimentAnalyzer


class SentimentalAnalyzer:
    def analyze(self, clause):
        self.perform_entity_level_analysis_of(clause)
        self.analyze_adverbial(clause)
        self.analyze_instrument_goal(clause)

        needs_to_be_verbally_analyzed = self.needs_to_be_verbally_analyzed(clause)
        if needs_to_be_verbally_analyzed: self.analyze_verbal(clause)

        self.analyze_isolated_adjectives(clause, needs_to_be_verbally_analyzed)

    def needs_to_be_verbally_analyzed(self, clause):
        suspend_assignation_classes = set(GlobalOperator.classes) - set(["negation", "future"])
        clause_classes = set([ go.klass for go in clause.global_operators ]) & suspend_assignation_classes
        return not bool(clause_classes)

    def analyze_isolated_adjectives(self, clause, needs_to_be_verbally_analyzed):
        IsolatedAdjectiveAnalyzer(clause, needs_to_be_verbally_analyzed).analyze()

    def analyze_verbal(self, clause):
        if clause.voice: VerbalSentimentAnalyzer(clause).analyze()

    def analyze_instrument_goal(self, clause):
        name = "instrument_goal"
        if not clause.has_structure(name): return

        structure = clause.structure(name)
        for entity in structure.entities:
            if clause.relative_entity == entity:
                header = clause.relative_linker[0]
            else:
                header = entity.source.header() if entity.is_linked() else entity.header()
            header_lemma = header.lemma
            if header_lemma in self.method_by_header:
                self.method_by_header[header_lemma](self, header_lemma, entity, clause)
            else:
                self.prepositional_assignation(header, entity, clause)

    def prepositional_assignation(self, header, entity, clause):
        valued_header = SentiWordNet.get(header.lemma)
        if valued_header.is_neutral(): return
        entity.sentimental_value.add_evidence(SentimentalValuedObject(header, valued_header.value))

    def instrument_assignation(self, header, entity, clause):
        self.assign_over_subject(entity, clause)

    def privative_assignation(self, header, entity, clause):
        self.assign_over_subject(entity, clause, 0.5, True)

    def assign_over_subject(self, entity, clause, coef = 1, reverse_polarity = False):
        if entity.sentimental_value.is_neutral(): return
        if not clause.has_structure("subject") or clause.structure("subject").is_empty(): return

        destination = clause.structure("subject").entity()

        entity_value = entity.sentimental_value.value
        if reverse_polarity: entity_value = (entity_value[1], entity_value[0])

        evidence = SentimentalValuedObject(entity, (int(coef * entity_value[0]), int(coef * entity_value[1])))
        destination.sentimental_value.add_evidence(evidence)

    def analyze_adverbial(self, clause):
        hints = clause.valuated_adverbs
        evidence = [ SentimentalValuedObject(adverb, SentiWordNet.get(adverb.lemma).value) for adverb in hints ]
        structures = [ "subject", "od" ]
        for structure in structures:
            if clause.has_structure(structure) and not clause.structure(structure).is_empty():
                entity = clause.structure(structure).entity()
                entity.sentimental_value.add_evidence(*evidence)
                break

    def perform_entity_level_analysis_of(self, clause):
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

    method_by_header = {"sin": privative_assignation, "con": instrument_assignation, "mediante": instrument_assignation,
                        "a_través_de": instrument_assignation, "por_medio_de": instrument_assignation }
