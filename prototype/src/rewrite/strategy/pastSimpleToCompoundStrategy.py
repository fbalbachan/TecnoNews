# -*- coding: utf-8 -*-
from src.rewrite.rewrite import Rewrite
from src.utils.stringUtils import set_first_letter_case


class PastSimpleToCompoundStrategy:
    def __init__(self, ontology):
        self.ontology = ontology

    def applies_to(self, clause):
        verb = clause.verb
        return clause.voice == "active" and not verb.has_compound_time() \
            and verb.matches_msi({ "mode" : "indicative", "time" : "pasado" }) and not verb.is_locution()

    def rewrite(self, clause):
        ontology = self.ontology
        verb = clause.verb

        inflected_leaf = verb.modal_verb() if verb.has_modal() else verb.leaf()

        haber_lf = ontology.get_lexical_form("haber", self.msi_for(inflected_leaf))
        participle_lf = ontology.get_lexical_form(inflected_leaf.lemma, self.participle_msi)

        rewrited_verb = haber_lf.text + " " + participle_lf.text
        if verb.has_modal(): rewrited_verb += " " + verb.leaf().lexical_form

        return Rewrite(verb.node, set_first_letter_case(verb.leaves()[0].original_lexical_form, rewrited_verb))

    def msi_for(self, verb):
        msi = verb.msi
        return { "mode" : "indicative", "time" : "presente", "person" : msi["person"], "number" : msi["number"]}

    participle_msi = { "mode" : "participio", "gender" : "masculine", "number" : "singular" }
