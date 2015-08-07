# -*- coding: utf-8 -*-
from src.rewrite.rewrite import Rewrite
from src.utils.stringUtils import set_first_letter_case


class PastCompoundToSimpleStrategy:
    def __init__(self, ontology):
        self.ontology = ontology

    def applies_to(self, clause):
        verb = clause.verb
        return clause.voice == "active" and verb.has_compound_time() \
            and verb.matches_msi({ "mode" : "indicative", "time" : "presente" }) and not verb.is_locution()

    def rewrite(self, clause):
        ontology = self.ontology
        verb = clause.verb

        inflected_leaf = verb.leaves()[0]
        action_leaf = verb.modal_verb() if verb.has_modal() else verb.leaf()

        lf = ontology.get_lexical_form(action_leaf.lemma, PastCompoundToSimpleStrategy.msi_for(inflected_leaf))

        rewritten_verb = lf.text
        if verb.has_modal():
            rewritten_verb += " " + verb.leaf().lexical_form

        return Rewrite.preserving_case(verb.node, rewritten_verb)

    @staticmethod
    def msi_for(verb):
        return {"mode": "indicative", "time": "pasado", "person": verb.person(), "number": verb.number()}

    type = "replacement"
