# -*- coding: utf-8 -*-
from src.rewrite.rewrite import Rewrite

class VerbalSynStrategy:
    def applies_to(self, clause):
        return clause.voice == "active"

    def rewrite(self, clause):
        verb = clause.verb
        return Rewrite(verb.node, "amó")

    type = "replacement"
