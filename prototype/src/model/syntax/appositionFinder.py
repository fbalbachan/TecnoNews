# -*- coding: utf-8 -*-
__author__ = 'Martin Caramés Abente'

debug_mode = False


class AppositionFinder:

    def __init__(self, clause):
        self.clause = clause

    def retrieve_appositions(self):
        if debug_mode: print "--> ClauseAnalyzer.retrieve_appositions(clause: ", self.clause, ")"

        candidate_entities = filter(lambda entity: entity.is_explicit()
                                                   and entity.category() == "noun"
                                                   and entity.node.label == "sn"
                                                   and self.entity_is_next_or_close_to(entity, [","], 1),
                                    self.clause.entities)

        candidate_entities = filter(lambda entity: entity.is_maximal_regarding(candidate_entities), candidate_entities)

        candidate_chains = self.group_entities_in_chains(candidate_entities)

        candidate_chains = filter(lambda chain: not self.is_enumeration(chain), candidate_chains)

        appositions = []
        for candidate_chain in candidate_chains:
            candidate_chain.sort(key=lambda p_entity: p_entity.token.start())

            if self.meets_chain_criteria_for_apposition(candidate_chain):
                final_chain = candidate_chain
            else:
                final_chain = self.find_maximal_sub_chain_meeting_criteria(self.meets_chain_criteria_for_apposition,
                                                                           candidate_chain)
            if final_chain:
                apposition = self.build_apposition(final_chain)
                appositions.append(apposition)

        return appositions

    def build_apposition(self, entity_chain):
        reference_entity = self.get_reference_entity(entity_chain)
        entities_in_apposition = filter(lambda p_entity: p_entity is not reference_entity, entity_chain)
        apposition = (reference_entity, entities_in_apposition)
        return apposition

    def find_maximal_sub_chain_meeting_criteria(self, criteria, chain):
        for i in range(len(chain)-1):
            for j in range(i+1, len(chain)):
                candidate = chain[i:j+1]
                if criteria(candidate):
                    return candidate

        return None

    def are_almost_siblings(self, entity_chain):
        levels = [entity.level() for entity in entity_chain]
        levels_set = set(levels)
        chain_in_right_hemiclause = self.clause.verb.node.position_of(entity_chain[0].node) == "right"
        return chain_in_right_hemiclause and len(levels_set) == 2 and levels[0] == levels[1]+1

    def meets_chain_criteria_for_apposition(self, candidate_chain):
        if len(candidate_chain) <= 1:
            return False

        are_siblings = all(entity.node.father == candidate_chain[0].node.father for entity in candidate_chain)
        entity_levels_are_ok = are_siblings or self.are_almost_siblings(candidate_chain)
        agree_in_per_gen_num = all(e.matches(candidate_chain[0]) for e in candidate_chain)

        there_is_place = any("semantic_classification" in e.msi
                             and e.msi["semantic_classification"] == "place" for e in candidate_chain)

        return entity_levels_are_ok and agree_in_per_gen_num and not there_is_place

    def get_reference_entity(self, chain):
        named = filter(lambda entity: "semantic_classification" in entity.msi
                                      and entity.msi["semantic_classification"], chain)
        return named[0] if named else chain[0]

    def entity_is_next_or_close_to(self, entity, lemmas, distance):
        """Checks the presence of a lemma (from lemmas) within distance from entity.

        :param lemmas: list of lemmas to look for.
        :param distance: number of (same level) nodes between the entity and the first lexical form
        :return: bool
        """

        if debug_mode: print "--> ClauseAnalyzer.entity_is_next_or_close_to(entity: ", entity, ", lemmas: ", lemmas, ")"

        is_next_to_lemma = self.entity_is_next_to(entity, lemmas)

        if is_next_to_lemma:
            return is_next_to_lemma

        is_close_but_not_next_to = self.entity_is_close_but_not_next_to(entity, lemmas, distance)
        return is_close_but_not_next_to

    def entity_is_next_to(self, entity, lemmas):
        """Checks the presence of a lemma (from lemmas) right next to the entity.

        :param lemmas: list of lemmas to look for.
        :return: bool
        """

        if debug_mode: print "--> ClauseAnalyzer.is_next_to_lexical_form(entity: ", entity, ", lemmas: ", lemmas, ")"

        clause_leaves = self.clause.proper_leaves()
        leaf_positions = {leaf: index for (index, leaf) in enumerate(clause_leaves)}

        last_leaf = entity.leaves()[-1]
        idx_last_leaf = leaf_positions[last_leaf]

        is_next_to_lemma = last_leaf.lemma in lemmas \
                           or len(clause_leaves) > idx_last_leaf+1 and clause_leaves[idx_last_leaf+1].lemma in lemmas

        return is_next_to_lemma

    def entity_is_close_but_not_next_to(self, entity, lemmas, distance):
        """Checks the presence of a lemma (from lemmas) within distance from entity.

        :param lemmas: list of lemmas to look for.
        :param distance: (in terms of the parse tree) Number of (same level) nodes between entity and the first lemma
        :return: bool
        """
        same_level_nodes = entity.node.father.children
        e_idx = same_level_nodes.index(entity.node)

        if distance <= 0 or len(same_level_nodes) <= e_idx+distance+1:
            return False

        middle_are_ok = True
        for idx in range(1, distance):
            middle_node = same_level_nodes[e_idx+idx]
            middle_are_ok = middle_are_ok and self.clause.same_hemiclause(middle_node, entity.node) \
                                          and not middle_node.label_lemma_matches([], ["y"])
        if not middle_are_ok:
            return False

        candidate1 = same_level_nodes[e_idx+distance+1]
        prev_node = same_level_nodes[e_idx+distance]
        candidate2 = prev_node.children[-1] if prev_node.children else None

        is_close = self.clause.same_hemiclause(candidate1, entity.node) \
                   and candidate1.label_lemma_matches(None, lemmas) \
                   or \
                   candidate2 and self.clause.same_hemiclause(candidate2, entity.node)\
                              and candidate2.label_lemma_matches(None, lemmas)
        return is_close

    def group_entities_in_chains(self, entities):
        inner_delimiters = [","]    # List of lexical forms to use as inner delimiters for each chain
        groups = []
        while len(entities) > 0:
            entity = entities.pop(0)
            group = self.pull_out_one_chain(entities, entity, inner_delimiters)
            groups.append(group)

        return groups

    def pull_out_one_chain(self, entities, entity, inner_delimiters):
        """

        :param entity: the entity from which the chain is built
        :param inner_delimiters: List of lexical forms to use as inner delimiters for the chain
        :return: entities in chain
        """
        consecutive = [entity]
        previous_length = 0
        while len(consecutive) > previous_length:
            previous_length = len(consecutive)
            for e in entities:
                if self.are_separated_by(consecutive[-1], e, inner_delimiters):
                    entities.remove(e)
                    consecutive.append(e)
                    break
                elif self.are_separated_by(e, consecutive[0], inner_delimiters):
                    entities.remove(e)
                    consecutive.insert(0, e)
                    break
                else:
                    continue

        return consecutive

    def are_separated_by(self, entity1, entity2, forms):
        clause_leaves = self.clause.proper_leaves()
        leaf_positions = {leaf: index for (index, leaf) in enumerate(clause_leaves)}

        last_leaf_first_entity = entity1.leaves()[-1]
        idx_last_leaf_first_entity = leaf_positions[last_leaf_first_entity]

        first_leaf_last_entity = entity2.leaves()[0]
        idx_first_leaf_last_entity = leaf_positions[first_leaf_last_entity]

        result = (last_leaf_first_entity.lexical_form in forms
                  and idx_last_leaf_first_entity+1 == idx_first_leaf_last_entity) \
                 or \
                 (len(clause_leaves) > idx_last_leaf_first_entity
                  and clause_leaves[idx_last_leaf_first_entity+1].lexical_form in forms
                  and idx_last_leaf_first_entity+2 == idx_first_leaf_last_entity)

        return result

    def is_enumeration(self, entities_chain):
        last_entity = entities_chain[-1]

        brothers = last_entity.node.father.children

        last_entity_idx = brothers.index(last_entity.node)

        if len(brothers) > last_entity_idx+1:
            result = brothers[last_entity_idx+1].label_lemma_matches(None, ["etcétera"])

            if not result and len(brothers) > last_entity_idx+2:
                result = brothers[last_entity_idx+1].label_lemma_matches(None, [","]) \
                         and brothers[last_entity_idx+2].label_lemma_matches(None, ["etcétera"])

            return result

        return False