# -*- coding: utf-8 -*-
from src.model.go.coordinatedNegationAnalyzer import CoordinatedNegationAnalyzer
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
        finders = [ NegativeParticleFinder ]
        for finder in finders:
            clause.global_operators.extend(finder(clause).find())

        print "--"
        print "Clause:", clause
        print "  global operators:", clause.global_operators
