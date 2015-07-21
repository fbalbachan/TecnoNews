# -*- coding: utf-8 -*-

class VerbalScript:
    def __init__(self, lemma, klass="NEUTRAL", agentive_coef=0, objective_coef=0):
        self.lemma = lemma
        self.klass = klass
        self.agentive_coef = agentive_coef
        self.objective_coef = objective_coef

    def __repr__(self):
        return self.lemma + " " + self.klass + (" " + str(self.agentive_coef) + "/" + str(self.objective_coef)) if \
            (self.agentive_coef != 0 or self.objective_coef != 0) else ""