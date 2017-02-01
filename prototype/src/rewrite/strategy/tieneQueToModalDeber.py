# -*- coding: utf-8 -*-
from src.rewrite.rewrite import Rewrite


class TieneQueToModalDeber:
    def __init__(self, ontology):
        self.ontology = ontology

    def applies_to(self, clause):
        verb = clause.verb
        return verb is not None and clause.voice == "active" and verb.is_modal_of("deber") and len(verb.leaves()) == 2 \
            and verb.leaves()[0].components()[1:] == ["que"]

    def rewrite(self, clause):
        ontology = self.ontology
        verb = clause.verb

        action_leaf = verb.leaf()

        lf = ontology.get_lexical_form("deber", TieneQueToModalDeber.msi_for(verb))

        rewritten_verb = lf.text + " " + repr(action_leaf)

        return Rewrite.preserving_case(verb.node, rewritten_verb)


    @staticmethod
    def msi_for(verb):
        msi = verb.msi
        return { attr: value for attr, value in msi.items() if attr in ["category", "number", "person", "mode", "time"] }

    type = "replacement"
