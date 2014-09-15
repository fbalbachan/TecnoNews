# -*- coding: utf-8 -*-
from src.rewrite.rewrite import Rewrite
from src.utils.stringUtils import set_first_letter_case


class FutureStrategy:
    def __init__(self, ontology):
        self.ontology = ontology

    def applies_to(self, clause):
        verb = clause.verb
        return clause.voice == "active" and verb.matches_msi({ "mode" : "indicative", "time" : "futuro" }) \
            and not verb.is_locution()

    def rewrite(self, clause):
        ontology = self.ontology
        verb = clause.verb
        leaf = verb.leaf()

        ir_lf = ontology.get_lexical_form("ir", self.msi_for(leaf))
        rewrited_verb = ir_lf.text + " a " + leaf.lemma

        return Rewrite(verb.node, set_first_letter_case(leaf.original_lexical_form, rewrited_verb))

    def msi_for(self, verb):
        msi = verb.msi
        return { "mode" : "indicative", "time" : "presente", "person" : msi["person"], "number" : msi["number"]}

    type = "replacement"
