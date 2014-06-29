# -*- coding: utf-8 -*-
from src.sentiment.sentiWordNet import SentiWordNet
from src.sentiment.sentimentalValuedObject import SentimentalValuedObject


class VerbalSentimentAnalyzer:
    def __init__(self, clause):
        self.clause = clause

    def analyze(self):
        verb = self.clause.verb
        verb_class = verb.sentimental_script.klass.lower()
        getattr(self, "analyze_" + verb_class)()

    def analyze_neutral(self):
        pass

    def analyze_equative(self):
        clause = self.clause
        if clause.structure("equative").is_empty() or clause.structure("subject").is_empty(): return

        destination = clause.structure("subject").entity()
        source = clause.structure("equative").entity()
        evidence = source.sentimental_value

        if clause.is_negated():
            evidence = SentimentalValuedObject(evidence.object, evidence.value)
            evidence.apply_coef(-0.5)

        destination.sentimental_value.add_evidence(evidence)

    def analyze_agentive(self):
        self.shed_on(1, "subject")

    def analyze_objective(self):
        self.shed_on(1, "od", "regimen", "oi")

    def analyze_dosaguas(self):
        self.analyze_dosaguas_or_switch()

    def analyze_switch(self):
        self.analyze_dosaguas_or_switch()

    def analyze_dosaguas_or_switch(self):
        script = self.clause.verb.sentimental_script
        self.shed_on(script.agentive_coef, "subject")
        self.shed_on(script.objective_coef, "od", "regimen", "oi")

    def shed_on(self, coef, *destinations):
        clause = self.clause
        verb = clause.verb
        valued = SentiWordNet.get(verb.lemma())
        if clause.is_negated(): coef = coef * -0.5

        for destination in destinations:
            if not clause.has_structure(destination) or clause.structure(destination).is_empty(): continue
            entity = clause.structure(destination).entity()

            evidence = SentimentalValuedObject(verb, valued.value)
            evidence.apply_coef(coef)

            entity.sentimental_value.add_evidence(evidence)
            break