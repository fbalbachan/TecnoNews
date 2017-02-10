# -*- coding: utf-8 -*-
from src.sentiment.sentiWordNet import SentiWordNet
from src.sentiment.sentimentalValuedObject import SentimentalValuedObject
from src.sentiment.verbalSentimentAnalyzer import VerbalSentimentAnalyzer


class IsolatedAdjectiveAnalyzer:
    def __init__(self, clause, needs_to_be_verbally_analyzed):
        self.clause = clause
        self.needs_to_be_verbally_analyzed = needs_to_be_verbally_analyzed

    def analyze(self):
        clause = self.clause
        current_go = None

        if not clause.has_structure("subject") or clause.structure("subject").is_empty():
            return

        destinations = [clause.structure("subject").entity()]

        coef = 1
        if clause.voice and clause.verb.transitivity == "EQUATIVE":
            if not self.needs_to_be_verbally_analyzed:
                return

            if clause.is_negated():
                coef = VerbalSentimentAnalyzer.NEGATION_COEF
                current_go = "negation"
            elif clause.has_global_operator_of("possibility", "volitive"):
                if clause.has_global_operator_of("possibility"):
                    current_go = "possibility"
                else:
                    current_go = "volitive"
                coef = VerbalSentimentAnalyzer.POSSIBILITY_COEF

            cataphoric_destination_subjects = self.cataphoric_destination_subjects()
            if cataphoric_destination_subjects:
                destinations = cataphoric_destination_subjects

        evidences = self.evidence_with(coef, current_go)
        for destination in destinations:
            destination.sentimental_value.add_evidence(*evidences)

    def evidence_with(self, coef, global_operator=None):
        evidences = []
        for hint in self.clause.isolated_adjectives:
            self.clause.false_entities.append(hint)
            valued = SentiWordNet.get(hint.lemma)
            if valued.is_neutral(): continue
            evidence = SentimentalValuedObject(hint, valued.value, global_operator)
            evidence.apply_coef(coef)

            evidences.append(evidence)
        return evidences

    def cataphoric_destination_subjects(self):
        if not self.clause.has_attr("pseudo_cataphoric"): return []
        clauses = filter(lambda clause: clause.is_subordinated_with("que") and clause.has_structure("subject") \
                      and not clause.structure("subject").is_empty(), self.clause.children)
        return [ clause.structure("subject").entity() for clause in clauses ]
