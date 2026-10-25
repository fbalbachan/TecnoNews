# -*- coding: utf-8 -*-
from src.ling.tacit_subjects import get_entity_some
from src.model.entity.tacitEntity import TacitEntity
from src.model.syntax.syntacticAnalyzer import SyntacticAnalyzer
from src.model.entity.animity import Animity

debug_mode = False


class PassiveVoiceSyntacticAnalyzer(SyntacticAnalyzer):
    def __init__(self, clause):
        SyntacticAnalyzer.__init__(self, clause)

    def subject(self):
        if debug_mode: print("--> PassiveVoiceSyntacticAnalyzer.subject()")
        at_right = lambda: self.search_subject_at("right", 4)
        at_left = lambda: self.search_subject_at("left", 4)

        verbal_animity = self.clause.verb.subject_animity
        entities = self.find_entities_by(at_right, at_left)
        entities = [entity for entity in entities if entity.animity_matches(verbal_animity)]
        if entities:
            entities[0].msi["animity"] = Animity.most_specific(verbal_animity, entities[0].msi["animity"])
            subject = [entities[0]]
        else:
            is_implicit = True
            subject = [get_entity_some(verbal_animity, is_implicit)]

        return subject

    def search_subject_at(self, side, distance):

        def which(node):
            first_leaf = node.leaves()[0]
            return first_leaf.msi["type"] == "preposition" \
                   and first_leaf.lexical_form == "por"

        return self.search_subord_at(side, distance, which)

    def od(self):
        # From domain knowledge we know that entities must be at: max distance left 6, max distance right 5
        # (insight come from oracle Fernando)

        if debug_mode: print("--> PassiveVoiceSyntacticAnalyzer.od()")
        verbal_animity = self.clause.verb.affected_object_animity
        entities = self.verb_matching_subject_entities(6, 5)
        entities = [entity for entity in entities if entity.animity_matches(verbal_animity)
                                         and (not self.starts_with_accepted_preposition(entity.node, "a")
                                              or Animity.animities_match(verbal_animity, Animity.animated))]
        if entities:
            od_entity = entities[0]
        else:
            od_entity = self.tacit_od()

        if "animity" in od_entity.msi:
            od_entity.msi["animity"] = Animity.most_specific(verbal_animity, od_entity.msi["animity"])

        return [od_entity]

    def tacit_od(self):
        if debug_mode: print("--> PassiveVoiceSyntacticAnalyzer.tacit_od()")
        verb = self.clause.verb
        pronoun = verb.matching_pronoun()
        pronoun_msi = verb.matching_pronoun_msi()
        pronoun_person = pronoun_msi['person']

        if pronoun_person in [1, 2]:
            pronoun_msi['animity'] = Animity.animated

        else:  # pronoun_person is 3:
            pronoun_msi['animity'] = Animity.bianimate

        return TacitEntity(pronoun, pronoun_msi)
