# -*- coding: utf-8 -*-
from src.model.syntacticAnalyzer import SyntacticAnalyzer
from src.model.syntacticStructure import SyntacticStructure
from src.model.tacitEntity import TacitEntity


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
        return TacitEntity("alguien", { "number" : "singular", "gender" : "neutral", "person" : 3 })

    def od(self):
        structure = SyntacticStructure("od")
        entities = self.nominal_and_personal_entities(3, 2)
        if entities:
            structure.entities = [ entities[0] ]
        else:
            structure.tacit_entities = [ self.tacit_od() ]
        return structure

    def tacit_od(self):
        verb = self.clause.verb
        return TacitEntity(verb.matching_pronoun(), verb.matching_pronoun_msi())
