# -*- coding: utf-8 -*-
from src.ling.gender import Gender
from src.ling.number import Number
from src.rewrite.rewrite import Rewrite


class RacontoStrategy:
    def __init__(self, ontology):
        self.ontology = ontology

    def applies_to(self, clause):
        clause_verb = clause.verb
        return clause_verb is not None and (clause_verb.matches_msi({"mode": "indicative"}) or clause_verb.matches_msi({"mode": "subjuntive"})) and not clause_verb.is_locution()# and clause.voice == 'active'

    def rewrite(self, clause):
        ontology = self.ontology
        if clause.voice == "active":
            #clause_verb = clause.node.nodes_with_labels("verb")
            clause_verb = clause.proper_tree().nodes_with_labels("verb")
        elif clause.voice == "passive":
            #clause_verb = clause.node.nodes_with_labels("vser")
            clause_verb = clause.proper_tree().nodes_with_labels("vser")
        else:
            clause_verb = []
        if len(clause_verb) == 0:
            return []
        clause_verb = clause_verb[0]

        rewriten_verb = ""
        for a_leaf in clause_verb.leaves():
            if ("time" not in a_leaf.msi or a_leaf.msi["time"] == "singular" or a_leaf.msi["time"] == "plural")\
                or (a_leaf.lemma == "haber" and a_leaf.msi["time"] == "presente")\
                or (a_leaf.msi["time"] not in ["presente", "pasado", "futuro"])\
                or (a_leaf.lemma == "ir"):

                rewriten_verb += " " + a_leaf.lexical_form

            elif a_leaf.msi["time"] == "pasado":
                haber_lf = ontology.get_lexical_form(
                    "haber",
                    {
                        "mode":  a_leaf.msi['mode'],
                        "time": "imperfecto",
                        "person": a_leaf.msi['person'],
                        "number": a_leaf.msi['number']
                    }
                )
                participle_lf = ontology.get_lexical_form(
                    a_leaf.lemma,
                    {
                        "mode": "participio",
                        "gender": "masculine",
                        "number": "singular"
                    }
                )
                if haber_lf is None or participle_lf is None:
                    return []
                rewriten_verb += " " + haber_lf.text + " " + participle_lf.text

            elif a_leaf.msi["time"] == "presente":
                past_lf = ontology.get_lexical_form(
                    a_leaf.lemma,
                    {
                        "mode":  a_leaf.msi['mode'],
                        "time": "imperfecto",
                        "person": a_leaf.msi['person'],
                        "number": a_leaf.msi['number']
                    }
                )
                rewriten_verb += " " + past_lf.text

            elif a_leaf.msi["time"] == "futuro" and a_leaf.msi["mode"] == "indicative":
                future_lf = ontology.get_lexical_form(
                    a_leaf.lemma,
                    {
                        "mode":  a_leaf.msi['mode'],
                        "time": "condicional",
                        "person": a_leaf.msi['person'],
                        "number": a_leaf.msi['number']
                    }
                )
                rewriten_verb += " " + future_lf.text

        if rewriten_verb != "":
            return Rewrite.preserving_case(clause_verb, rewriten_verb)
        else:
            return []


    type = "replacement"
