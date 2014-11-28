# -*- coding: utf-8 -*-
from src.ling.tacit_subjects import implicit_somebody
from src.model.entity.tacitEntity import TacitEntity
from src.model.syntax.syntacticAnalyzer import SyntacticAnalyzer
from src.model.syntax.syntacticStructure import SyntacticStructure


class PassiveVoiceSyntacticAnalyzer(SyntacticAnalyzer):
    def __init__(self, clause):
        SyntacticAnalyzer.__init__(self, clause)

    def subject(self):
        at_right = lambda: self.search_subject_at("right", 3)
        at_left  = lambda: self.search_subject_at("left", 3)

        entities = self.find_entities_by(at_right, at_left)
        return [ entities[0] ] if entities else [ implicit_somebody() ]

    def search_subject_at(self, side, distance):
        def which(node):
            first_leaf = node.leaves()[0]
            return first_leaf.msi["type"] == "preposition" and first_leaf.lexical_form == "por"
        return self.search_subord_at(side, distance, which)

    def od(self):
        # From domain knowledge we know the the entities musty be at:
        # max distance left 6, max distance left distance right 5
        # Insight come from oracle Fernando
        entities = self.verb_matching_subject_entities(6, 5)
        return [ entities[0] ] if entities else [ self.tacit_od() ]

    def tacit_od(self):
        verb = self.clause.verb
        return TacitEntity(verb.matching_pronoun(), verb.matching_pronoun_msi())
