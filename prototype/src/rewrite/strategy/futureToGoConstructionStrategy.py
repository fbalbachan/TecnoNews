# -*- coding: utf-8 -*-
from src.rewrite.rewrite import Rewrite
from src.utils.stringUtils import set_first_letter_case


class FutureToGoConstructionStrategy:
    def __init__(self, ontology):
        self.ontology = ontology

    def applies_to(self, clause):
        verb = clause.verb
        return clause.voice == "active" and not verb.is_compound() and \
            verb.matches_msi({"mode": "indicative", "time": "futuro"}) and not verb.is_locution()

    def rewrite(self, clause):
        ontology = self.ontology
        verb = clause.verb
        leaf = verb.leaf()

        ir_lf = ontology.get_lexical_form("ir", FutureToGoConstructionStrategy.msi_for(leaf))
        rewritten_verb = ir_lf.text + " a " + leaf.lemma

        return Rewrite.preserving_case(verb.node, rewritten_verb)


    @staticmethod
    def msi_for(verb):
        msi = verb.msi
        return {"mode": "indicative", "time": "presente", "person": msi["person"], "number": msi["number"]}

    type = "replacement"
