# -*- coding: utf-8 -*-
from src.ling.tacit_subjects import somebody
from src.model.entity.tacitEntity import TacitEntity
from src.model.syntax.syntacticAnalyzer import SyntacticAnalyzer
from src.model.syntax.syntacticStructure import SyntacticStructure


class PassiveVoiceSyntacticAnalyzer(SyntacticAnalyzer):
    def __init__(self, clause):
        SyntacticAnalyzer.__init__(self, clause)

    def subject(self):
        structure = SyntacticStructure("subject")

        at_right = lambda: self.search_subject_at("right", 3)
        at_left  = lambda: self.search_subject_at("left", 3)

        entities = self.find_entities_by([at_right, at_left])
        if entities:
            structure.entities = [ entities[0] ]
        else:
            structure.tacit_entities = [ self.tacit_subject() ]

        return structure

    def search_subject_at(self, side, distance):
        def which(node):
            first_leaf = node.leaves()[0]
            return first_leaf.msi["type"] == "preposition" and first_leaf.lexical_form.lower() == "por"
        return self.search_subord_at(side, distance, which)

    def tacit_subject(self):
        return somebody()

    def od(self):
        structure = SyntacticStructure("od")
        entities = self.verb_matching_subject_entities(3, 2)
        if entities:
            structure.entities = [ entities[0] ]
        else:
            structure.tacit_entities = [ self.tacit_od() ]
        return structure

    def tacit_od(self):
        verb = self.clause.verb
        return TacitEntity(verb.matching_pronoun(), verb.matching_pronoun_msi())
