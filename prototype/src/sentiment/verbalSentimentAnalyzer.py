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
        if clause.structure("equative").is_empty() or clause.structure("subject").is_empty():
            return

        destination = clause.structure("subject").entity()
        source = clause.structure("equative").entity()
        evidence = source.sentimental_value

        current_go = None
        if clause.is_negated():
            evidence = SentimentalValuedObject.cloned(evidence, self.NEGATION_COEF, "negation")
        elif clause.has_global_operator_of("possibility", "volitive"):
            if clause.has_global_operator_of("possibility"):
                evidence = SentimentalValuedObject.cloned(evidence, self.POSSIBILITY_COEF, "possibility")
            else:
                evidence = SentimentalValuedObject.cloned(evidence, self.POSSIBILITY_COEF, "volitive")

        destination.sentimental_value.add_evidence(evidence)

    def analyze_agentive(self):
        self.shed_on(1, "subject")

    def analyze_objective(self):
        self.shed_on(1, "od", "regimen", "oi")

    def analyze_dosaguas(self):
        script = self.clause.verb.sentimental_script
        self.analyze_dosaguas_or_switch(script.agentive_coef, script.objective_coef)

    def analyze_switch(self):
        script = self.clause.verb.sentimental_script
        objective_coef = script.objective_coef
        if self.clause.is_negated(): objective_coef = abs(objective_coef)
        self.analyze_dosaguas_or_switch(script.agentive_coef, objective_coef)

    def analyze_dosaguas_or_switch(self, agentive_coef, objective_coef):
        self.shed_on(agentive_coef, "subject")
        self.shed_on(objective_coef, "od", "regimen", "oi")

    def shed_on(self, coef, *destinations):
        clause = self.clause
        verb = clause.verb
        valued = SentiWordNet.get(verb.lemma())

        current_go = None
        if clause.is_negated():
            coef = coef * self.NEGATION_COEF
            current_go = "negation"
        elif clause.has_global_operator_of("possibility", "volitive"):
            coef = coef * self.POSSIBILITY_COEF
            if clause.has_global_operator_of("possibility"):
                current_go = "possibility"
            else:
                current_go = "volitive"

        for destination in destinations:
            if not clause.has_structure(destination) or clause.structure(destination).is_empty(): continue
            entity = clause.structure(destination).entity()

            evidence = SentimentalValuedObject(verb, valued.value, current_go)
            evidence.apply_coef(coef)

            entity.sentimental_value.add_evidence(evidence)
            break

    NEGATION_COEF = -0.5
    POSSIBILITY_COEF = 0.1

