# -*- coding: utf-8 -*-

from src.ling.tacit_subjects import this, get_entity_some, impersonal_somebody
from src.model.entity.tacitEntity import TacitEntity
from src.model.syntax.syntacticAnalyzer import SyntacticAnalyzer
from src.model.entity.entity import Entity
from src.model.entity.animityEnum import AnimityEnum


class ActiveVoiceSyntacticAnalyzer(SyntacticAnalyzer):
    def __init__(self, clause):
        SyntacticAnalyzer.__init__(self, clause)

    def analyze(self, clause):
        # print "Entering ActiveVoiceSyntacticAnalyzer.analyze(). Verb: ", str(clause.verb)

        if self.there_is_an_impersonal_se():
            pre_subject = self.subject_without_animity_restrictions()
            pre_od = self.od_without_animity_restrictions()

            is_impersonal_passive = ActiveVoiceSyntacticAnalyzer.is_impersonal_passive(pre_subject)
            is_impersonal_not_passive = ActiveVoiceSyntacticAnalyzer.is_impersonal_not_passive(pre_subject, pre_od)

            if is_impersonal_passive or is_impersonal_not_passive:
                self.analyze_impersonal_se(is_impersonal_passive, pre_subject, pre_od)
                return

        super(ActiveVoiceSyntacticAnalyzer, self).analyze(clause)

    def there_is_an_impersonal_se(self):
        # print "Entering ActiveVoiceSyntacticAnalyzer.there_is_an_impersonal_se()"
        there_is = self.clause.verb.transitivity is "TRANSITIVE" \
                   and self.there_is_se_before_verbal_tree()

        return there_is

    def analyze_impersonal_se(self, is_impersonal_passive, pre_subject, pre_od):
        clause = self.clause
        for structure in clause.syntactic_structures:
            slot_name = structure.name
            if structure.is_empty():
                if slot_name == 'subject':
                    is_impersonal = True
                    entities = [get_entity_some(AnimityEnum.animated, False, is_impersonal)]

                elif slot_name == 'od':
                    entities = pre_subject if is_impersonal_passive else pre_od

                else:
                    method_get_slot_entities = getattr(self, slot_name, lambda: [])
                    entities = method_get_slot_entities()

                structure.append_all(entities)

    def there_is_se_before_verbal_tree(self):
        # print "Entering ActiveVoiceSyntacticAnalyzer.there_is_se_before_verbal_tree()"
        verb_node = self.clause.verb.node
        brothers = verb_node.father.children

        while brothers and (brothers[0].label != "morfema-verbal"
                            or len(brothers[0].children) == 0
                            or str(brothers[0].children[0]).lower() != "se"):
            brothers.pop(0)

        there_is = any([brothers[1].contains(leaf) for leaf in self.clause.verb.leaves()])

        return there_is

    @staticmethod
    def is_impersonal_passive(subject):
        is_impersonal_passive = subject and subject[0].is_explicit() \
                                        and subject[0].msi["animity"] is AnimityEnum.inanimate
        return is_impersonal_passive

    @staticmethod
    def is_impersonal_not_passive(subject, od):
        still_not_passive = od and (not subject or subject[0].is_tacit() or subject[0].is_implicit())
        if still_not_passive:
            explicit = od[0].is_explicit()
            still_not_passive = od[0].is_explicit() and od[0].msi["animity"] is AnimityEnum.animated

        return still_not_passive

    def subject(self):
        # print "Entering ActiveVoiceSyntacticAnalyzer.subject()"

        clause = self.clause
        if clause.is_gerund():
            subject = []
            return subject

        verbal_animity = clause.verb.subject_animity
        entities = self.verb_matching_subject_entities(5, 4)
        entities = SyntacticAnalyzer.filter_by_animity(entities, verbal_animity)

        if entities:
            entities[0].msi["animity"] = AnimityEnum.most_specific(verbal_animity, entities[0].msi["animity"])
            subject = [entities[0]]

        else:
            subject = [self.tacit_or_implicit_subject(verbal_animity)]

        return subject

    def subject_without_animity_restrictions(self):
        # print "Entering ActiveVoiceSyntacticAnalyzer.subject_without_animity_restrictions()"

        clause = self.clause
        if clause.is_gerund():
            subject = []
            return subject

        forward = False
        entities = self.verb_matching_subject_entities(4, 5, forward)

        if entities:
            subject = [entities[0]]
        else:
            subject = [self.tacit_or_implicit_subject()]

        return subject

    def tacit_or_implicit_subject(self, verbal_animity=AnimityEnum.bianimate):
        # print "Subject is tacit or implicit"

        if self.is_root_relative_clause():
            is_implicit = True
            entity_some = get_entity_some(verbal_animity, is_implicit)
            return entity_some

        if self.clause.has_kind_of_cataphoric_structure():
            return this()

        return self.tacit_subject(verbal_animity)

    def is_root_relative_clause(self):
        clause = self.clause
        return clause.is_relative() and clause.is_root()

    def tacit_subject(self, verbal_animity=AnimityEnum.bianimate):
        verb = self.clause.verb
        pronoun = verb.matching_pronoun()
        pronoun_msi = verb.matching_pronoun_msi()
        pronoun_msi['animity'] = AnimityEnum.animated if pronoun_msi['person'] in [1, 2] else verbal_animity

        return TacitEntity(pronoun, pronoun_msi)

    def od(self):
        # print "Entering ActiveVoiceSyntacticAnalyzer.od()"
        verbal_animity = self.clause.verb.affected_object_animity

        [nominal_entities_at_same_level_nodes,
         nominal_entities_under_prep_a, pronominal_entities] = self.get_od_candidate_entities(verbal_animity)

        candidate_entities = nominal_entities_at_same_level_nodes \
                             + nominal_entities_under_prep_a \
                             + pronominal_entities

        candidate_entities_matching_anim = nominal_entities_at_same_level_nodes \
                                  + SyntacticAnalyzer.filter_by_animity(nominal_entities_under_prep_a, verbal_animity) \
                                  + pronominal_entities

        od = self.search_od(candidate_entities, candidate_entities_matching_anim, verbal_animity)

        return od

    def search_od(self, candidate_entities, candidate_entities_matching_anim, verbal_animity=AnimityEnum.bianimate):
        # print "Entering ActiveVoiceSyntacticAnalyzer.search_od()"
        if not candidate_entities:
            is_implicit = True
            return [get_entity_some(verbal_animity, is_implicit)]

        if not candidate_entities[0].is_subordinated_with_preposition("a"):
            return [candidate_entities[0]]

        linked = self.link_duplicated_od_for(candidate_entities)
        if linked:
            return [candidate_entities[0], linked]

        if not candidate_entities_matching_anim:
            is_implicit = True
            return [get_entity_some(verbal_animity, is_implicit)]

        return [candidate_entities_matching_anim[0]]

    def get_od_candidate_entities(self, verbal_animity=AnimityEnum.bianimate):
        # print "Entering ActiveVoiceSyntacticAnalyzer.get_od_candidate_entities()"
        nominal_entities_at_same_level_nodes = \
            self.find_entities_by(lambda: self.search_nominal_od_at_same_level_nodes("right", 4, verbal_animity),
                                  lambda: self.search_nominal_od_at_same_level_nodes("left", 3, verbal_animity))

        nominal_entities_under_prep_a = \
            self.find_entities_by(lambda: self.search_nominal_od_under_prep_a("right", 4),
                                  lambda: self.search_nominal_od_under_prep_a("left", 3))
        pronominal_entities = \
            self.find_entities_by(lambda: self.search_pronoun_at("right", 3, verbal_animity),
                                  lambda: self.search_pronoun_at("left", 3, verbal_animity))

        return [nominal_entities_at_same_level_nodes,
                nominal_entities_under_prep_a,
                pronominal_entities]

    def link_duplicated_od_for(self, od_candidates):
        # print "Entering ActiveVoiceSyntacticAnalyzer.link_duplicated_od_for()"
        accusative_pronoun = self.search_duplicated_od_for(od_candidates[0])
        if accusative_pronoun is not None:
            accusative_pronoun.add_coreference(od_candidates[0])
            od_candidates.append(accusative_pronoun)

        return accusative_pronoun

    def search_duplicated_od_for(self, source_od):
        """

        :rtype: TacitEntity
        """

        # print "Entering ActiveVoiceSyntacticAnalyzer.search_duplicated_od_for()"
        closest_entities = self.clause.entities_closest_to_verb(("left", 3), ("right", 2))
        matching_pronouns = self.only_accusative_pronouns_of(closest_entities)
        matching_pronouns = filter(lambda pronoun: source_od.matches(pronoun), matching_pronouns)

        if len(matching_pronouns) > 1:
            raise Exception("Se encontró más de un pronombre duplicando el OD.")

        if not matching_pronouns:
            return None

        result = matching_pronouns[0] if matching_pronouns[0] != source_od else None

        return result

    def od_without_animity_restrictions(self):
        # print "Entering ActiveVoiceSyntacticAnalyzer.od_without_animity_restrictions()"
        [nominal_entities_at_same_level_nodes,
         nominal_entities_under_prep_a, pronominal_entities] = self.get_od_candidate_entities()

        candidate_entities = nominal_entities_at_same_level_nodes \
                             + nominal_entities_under_prep_a \
                             + pronominal_entities

        od = self.search_od(candidate_entities, candidate_entities)

        return od

    def oi(self):
        # print "Entering ActiveVoiceSyntacticAnalyzer.oi()"
        entities = self.find_entities_by(lambda: self.search_nominal_oi_at("right", 3, AnimityEnum.animated),
                                         lambda: self.search_nominal_oi_at("left", 3, AnimityEnum.animated),
                                         lambda: self.search_pronoun_at("left", 2, AnimityEnum.animated),
                                         lambda: self.search_pronoun_at("right", 2, AnimityEnum.animated))
        if entities:
            entities[0].msi["animity"] = AnimityEnum.most_specific(entities[0].msi["animity"], AnimityEnum.animated)

        candidates = [entities[0]] if entities else []
        return candidates

    def regimen(self):
        # print "Entering ActiveVoiceSyntacticAnalyzer.regimen()"
        verbal_animity = self.clause.verb.affected_object_animity
        entities = self.get_regimen_candidate_entities(verbal_animity)
        if entities:
            entities[0].msi["animity"] = AnimityEnum.most_specific(entities[0].msi["animity"], verbal_animity)
        candidates = [entities[0]] if entities else []
        return candidates

    def get_regimen_candidate_entities(self, verbal_animity):
        at_right = lambda: self.search_regime_at("right", 3, verbal_animity)
        at_left = lambda: self.search_regime_at("left", 2, verbal_animity)
        entities = self.find_entities_by(at_right, at_left)
        return entities

    def search_regime_at(self, side, distance, verbal_animity):
        entities = self.search_subords_with_prep_at(side, distance, "a", "por", "en", "de", "contra", "con", "sobre")
        entities = SyntacticAnalyzer.filter_by_animity(entities, verbal_animity)
        candidates = [entities[0]] if entities else []
        return candidates

    def equative(self):
        # print "Entering ActiveVoiceSyntacticAnalyzer.equative()"
        verbal_animity = self.clause.verb.affected_object_animity
        entities = self.get_equative_candidate_entities(verbal_animity)
        if entities:
            entities[0].msi["animity"] = AnimityEnum.most_specific(entities[0].msi["animity"], verbal_animity)
        candidates = [entities[0]] if entities else []
        return candidates

    def get_equative_candidate_entities(self, verbal_animity):
        entities = self.valid_subject_entities(2, 3) \
                  + self.search_subords_with_prep_at("right", 3, "de", "para")
        entities = SyntacticAnalyzer.filter_by_animity(entities, verbal_animity)
        return entities

    def search_nominal_oi_at(self, side, distance, animity=AnimityEnum.bianimate):
        # print "Entering ActiveVoiceSyntacticAnalyzer.search_nominal_oi_at()"
        entities = self.search_subords_with_prep_at(side, distance, "a", "para")
        entities = Entity.only_maximal(entities)
        entities = SyntacticAnalyzer.filter_infinitives(entities)
        entities = SyntacticAnalyzer.filter_by_animity(entities, animity)
        return entities

    def search_nominal_od_at_same_level_nodes(self, side, distance, verbal_animity=AnimityEnum.bianimate):
        entities = self.clause.entities_closest_to_verb_at(side, distance)
        entities = self.only_nominal_of(entities)
        entities = SyntacticAnalyzer.filter_by_animity(entities, verbal_animity)
        return entities

    def search_nominal_od_under_prep_a(self, side, distance, verbal_animity=AnimityEnum.bianimate):
        entities = self.search_subords_with_prep_at(side, distance, "a")
        entities = Entity.only_maximal(entities)
        entities = SyntacticAnalyzer.filter_infinitives(entities)
        entities = SyntacticAnalyzer.filter_by_animity(entities, verbal_animity)
        return entities
