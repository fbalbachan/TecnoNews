# -*- coding: utf-8 -*-
from src.model.go.VerbsWithSubordinatedFinder import VerbsWithSubordinatedFinder
from src.model.go.VolitiveModalityFinder import VolitiveModalityFinder
from src.model.go.conditionAnalyzer import ConditionAnalyzer
from src.model.go.coordinatedNegationAnalyzer import CoordinatedNegationAnalyzer
from src.model.go.globalOperator import GlobalOperator
from src.model.go.negativeParticleFinder import NegativeParticleFinder
from src.model.go.totalQuestionAnalyzer import TotalQuestionAnalyzer


class GlobalOperatorAnalyzer:

    def __init__(self, sentence):
        self.sentence = sentence
        self.setup_finders()

    def analyze(self):
        sentence_analyzers = [ CoordinatedNegationAnalyzer, TotalQuestionAnalyzer, ConditionAnalyzer ]
        for analyzer in sentence_analyzers:
            analyzer(self.sentence).analyze()

        for clause in self.sentence.clauses:
            self.analyze_clause(clause)

    def analyze_clause(self, clause):
        for finder in self.finders:
            found = finder(clause)
            if found: clause.global_operators.update(found)

        print "Clause:", clause
        print "  global operators:", clause.global_operators
        print "--"

    def setup_finders(self):
        self.finders = [ self.negation_finder, self.conditional_verb_finder, self.imperative_finder,
            self.possibility_word_finder, self.subjuntive_finder, self.verb_poder_finder, self.deontic_modality_finder,
            self.future_finder, self.volitive_finder, self.verbs_with_subordinated_finder ]

    def verbs_with_subordinated_finder(self, clause):
        return VerbsWithSubordinatedFinder(clause).find()

    def volitive_finder(self, clause):
        return VolitiveModalityFinder(clause).find()

    def future_finder(self, clause):
        if clause.voice:
            verb_leaves = clause.verb.leaves
            lemmas = [ leaf.lemma for leaf in clause.verb.node.leaves() ]
            print lemmas
            leaf = verb_leaves[0]
            if (leaf.msi["time"] == "futuro" and leaf.msi["mode"] == "indicative") or lemmas[:2] == ["ir", "a"]:
                return [ GlobalOperator("future", clause.verb)]

    def deontic_modality_finder(self, clause):
        if clause.voice:
            leaf = clause.verb.leaves[0]
            if leaf.lemma == "deber" and leaf.size() == 2 and leaf.components()[1] == "que":
                return [ GlobalOperator("imperative", clause.verb)]

    def verb_poder_finder(self, clause):
        if clause.voice and clause.verb.leaves[0].lemma == "poder":
            return [ GlobalOperator("possibility", clause.verb)]

    def subjuntive_finder(self, clause):
        if clause.voice and clause.verb.leaves[0].msi["mode"] == "subjuntive" and (clause.is_relative() or \
            (clause.is_subordinated() and clause.proper_leaves()[0].lemma == "cuando")):
            return [ GlobalOperator("possibility", clause.verb)]

    def possibility_word_finder(self, clause):
        possibility_forms = [ "probablemente", "posiblemente", "supuestamente", "aparentemente", "tal_vez", "acaso",
                             "quizá", "quizás" ]
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