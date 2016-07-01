# -*- coding: utf-8 -*-
from src.ling.gender import Gender
from src.ling.number import Number
from src.rewrite.rewrite import Rewrite


class RacontoStrategy:
    def __init__(self, ontology):
        self.ontology = ontology

    def applies_to(self, clause):
        clause_verb = clause.verb
        return (clause_verb.matches_msi({"mode": "indicative"}) or clause_verb.matches_msi({"mode": "subjuntive"})) and not clause_verb.is_locution() and not clause_verb.is_compound()

    def rewrite(self, clause):
        ontology = self.ontology
        clause_verb = clause.verb

        inflected_leaf = clause_verb.modal_verb() if clause_verb.has_modal() else clause_verb.leaf()
        if clause_verb.matches_msi({"time": "pasado"}):
            haber_lf = ontology.get_lexical_form(
                "haber",
                {
                    "mode":  clause_verb.msi['mode'],
                    "time": "imperfecto",
                    "person": clause_verb.msi['person'],
                    "number": clause_verb.msi['number']
                }
            )
            participle_lf = ontology.get_lexical_form(
                inflected_leaf.lemma,
                {
                    "mode": "participio",
                    "gender": "masculine",
                    "number": "singular"
                }
            )
            return Rewrite.preserving_case(clause_verb.node, haber_lf.text + " " + participle_lf.text)

        elif clause_verb.matches_msi({"time": "presente"}):
            past_lf = ontology.get_lexical_form(
                inflected_leaf.lemma,
                {
                    "mode":  clause_verb.msi['mode'],
                    "time": "pasado",
                    "person": clause_verb.msi['person'],
                    "number": clause_verb.msi['number']
                }
            )
            return Rewrite.preserving_case(clause_verb.node, past_lf.text)


    type = "replacement"
