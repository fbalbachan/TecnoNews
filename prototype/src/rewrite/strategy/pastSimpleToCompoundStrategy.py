# -*- coding: utf-8 -*-
from src.ling.gender import Gender
from src.ling.number import Number
from src.rewrite.rewrite import Rewrite


class PastSimpleToCompoundStrategy:
    def __init__(self, ontology):
        self.ontology = ontology

    def applies_to(self, clause):
        verb = clause.verb
        return clause.voice == "active" \
               and not verb.has_compound_time() \
               and verb.matches_msi({"mode": "indicative", "time": "pasado"}) \
               and not verb.is_locution()

    def rewrite(self, clause):
        ontology = self.ontology
        verb = clause.verb

        inflected_leaf = verb.modal_verb() if verb.has_modal() else verb.leaf()

        haber_lf = ontology.get_lexical_form("haber", PastSimpleToCompoundStrategy.msi_for(inflected_leaf))
        participle_lf = ontology.get_lexical_form(inflected_leaf.lemma, self.participle_msi)

        rewritten_verb = haber_lf.text + " " + participle_lf.text
        if verb.has_modal():
            rewritten_verb += " " + verb.leaf().lexical_form

        return Rewrite.preserving_case(verb.node, rewritten_verb)

    @staticmethod
    def msi_for(verb):
        return {"mode": "indicative",    "time": "presente",
                "person": verb.msi['person'], "number": verb.msi['number']}

    participle_msi = {"mode": "participio",
                      "gender": Gender.masculine,
                      "number": Number.singular}

    type = "replacement"
