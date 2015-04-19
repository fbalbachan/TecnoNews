# -*- coding: utf-8 -*-
from src.rewrite.rewrite import Rewrite
from src.utils.stringUtils import set_first_letter_case


class GoConstructionToFutureStrategy:
    def __init__(self, ontology):
        self.ontology = ontology

    def applies_to(self, clause):
        verb = clause.verb
        return clause.voice == "active" and len(verb.leaves()) == 2 and verb.leaves()[0].lemma == "ir" and \
            verb.matches_msi({ "mode" : "indicative", "time" : "presente" }) and not verb.is_locution()

    def rewrite(self, clause):
        ontology = self.ontology
        verb = clause.verb
        ir_leaf = verb.leaves()[0]

        rewritten_verb = ontology.get_lexical_form(verb.lemma(), GoConstructionToFutureStrategy.msi_for(ir_leaf)).text

        return Rewrite.preserving_case(verb.node, rewritten_verb)

    @staticmethod
    def msi_for(verb):
        msi = verb.msi
        return {"mode": "indicative", "time": "futuro", "person": msi["person"], "number": msi["number"]}

    type = "replacement"
