# -*- coding: utf-8 -*-
from src.rewrite.rewrite import Rewrite
from src.utils.stringUtils import set_first_letter_case

# Ejemplo de acción de la estrategia:
# "Ellos van a condenar al preso." -> "Ellos condenarán al detenido."

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
        #return {"mode": "indicative", "time": "futuro",
        #        "person": verb.person(), "number": verb.number()}
        return {"mode": "indicative", "time": "futuro",
                "person": verb.msi['person'], "number": verb.msi['number']}


    type = "replacement"
