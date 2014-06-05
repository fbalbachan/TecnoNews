# -*- coding: utf-8 -*-
from src.model.go.coordinatedNegationAnalyzer import CoordinatedNegationAnalyzer
from src.model.go.globalOperator import GlobalOperator
from src.model.go.negativeParticleFinder import NegativeParticleFinder


class GlobalOperatorAnalyzer:

    def __init__(self, sentence):
        self.sentence = sentence

    def analyze(self):
        sentence_analyzers = [ CoordinatedNegationAnalyzer ]
        for analyzer in sentence_analyzers:
            analyzer(self.sentence).analyze()

        for clause in self.sentence.clauses:
            self.analyze_clause(clause)

    def analyze_clause(self, clause):
        finders = [ self.negation_finder, self.conditional_verb_finder, self.imperative_finder,
                   self.possibility_word_finder, self.subjuntive_in_relative_finder ]

        for finder in finders:
            found = finder(clause)
            if found: clause.global_operators.extend(found)

        print "--"
        print "Clause:", clause
        print "  global operators:", clause.global_operators

    def subjuntive_in_relative_finder(self, clause):
        if clause.voice and clause.verb.leaves[0].msi["mode"] == "subjuntive" and clause.is_relative():
            return [ GlobalOperator("possibility", clause.verb)]

    def possibility_word_finder(self, clause):
        possibility_forms = [ "probablemente", "posiblemente", "supuestamente", "aparentemente" ]
        leaves = filter(lambda leaf: leaf.lexical_form in possibility_forms, clause.proper_leaves())
        return [ GlobalOperator("possibility", leaf) for leaf in leaves ]

    def imperative_finder(self, clause):
        if clause.voice and clause.verb.leaves[0].msi["mode"] == "imperative":
            return [ GlobalOperator("imperative", clause.verb)]

    def conditional_verb_finder(self, clause):
        if clause.voice and clause.verb.leaves[0].msi["time"] == "condicional":
            return [ GlobalOperator("possibility", clause.verb)]

    def negation_finder(self, clause):
        return NegativeParticleFinder(clause).find()