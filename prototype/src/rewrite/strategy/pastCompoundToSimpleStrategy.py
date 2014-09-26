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

        lf = ontology.get_lexical_form(action_leaf.lemma, self.msi_for(inflected_leaf))

        rewrited_verb = lf.text
        if verb.has_modal(): rewrited_verb += " " + verb.leaf().lexical_form

        return Rewrite.preserving_case(verb.node, rewrited_verb)

    def msi_for(self, verb):
        msi = verb.msi
        return { "mode" : "indicative", "time" : "pasado", "person" : msi["person"], "number" : msi["number"]}

    type = "replacement"
