# -*- coding: utf-8 -*-
from src.rewrite.rewrite import Rewrite
from src.utils.stringUtils import set_first_letter_case


class SubjuntiveImperfectStrategy:
    def __init__(self, ontology):
        self.ontology = ontology

    def applies_to(self, clause):
        verb = clause.verb
        return clause.voice == "active" and verb.matches_msi({ "mode" : "subjuntive", "time" : "imperfecto" }) \
            and not verb.is_locution()

    def rewrite(self, clause):
        ontology = self.ontology
        verb = clause.verb
        leaf = verb.leaf()

        lexical_forms = ontology.get_lexical_forms(leaf.lemma, self.msi_for(leaf))
        rewrited_verb = filter(lambda lf: lf.text != leaf.lexical_form, lexical_forms)[0].text

        return Rewrite(verb.node, set_first_letter_case(leaf.original_lexical_form, rewrited_verb))

    def msi_for(self, verb):
        msi = verb.msi
        return { "mode" : "subjuntive", "time" : "imperfecto", "person" : msi["person"], "number" : msi["number"]}
