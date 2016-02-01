# -*- coding: utf-8 -*-
from src.rewrite.rewrite import Rewrite
from src.utils.stringUtils import set_first_letter_case


class SubjunctiveImperfectStrategy:
    def __init__(self, ontology):
        self.ontology = ontology

    def applies_to(self, clause):
        verb = clause.verb
        return clause.voice == "active" and verb.matches_msi({"mode": "subjunctive", "time" : "imperfecto"}) \
            and not verb.is_locution()

    def rewrite(self, clause):
        ontology = self.ontology
        verb = clause.verb
        leaf = verb.leaf()

        lexical_forms = ontology.get_lexical_forms(leaf.lemma, SubjunctiveImperfectStrategy.msi_for(leaf))
        rewritten_verb = filter(lambda lf: lf.text != leaf.lexical_form, lexical_forms)[0].text

        return Rewrite.preserving_case(verb.node, rewritten_verb)

    @staticmethod
    def msi_for(verb):
        #return {"mode": "subjunctive", "time": "imperfecto",
        #        "person": verb.person(), "number": verb.number()}
        return {"mode": "subjunctive", "time": "imperfecto",
                "person": verb.msi['person'], "number": verb.msi['number']}


    type = "replacement"
