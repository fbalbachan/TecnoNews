# -*- coding: utf-8 -*-
__author__ = 'Martin Caramés Abente'


class AppositionFinder:

    def __init__(self, clause):
        debug_mode = False
        self.clause = clause

    def retrieve_appositions(self):
        # print "Entering ClauseAnalyzer.retrieve_appositions(clause: ", self.clause, ")"

        candidate_entities = filter(lambda entity: entity.is_explicit()
                                                   and entity.category() == "noun"
                                                   and entity.node.label == "sn"
                                                   and self.is_close_to_lexical_form(entity, [","], 1),
                                    self.clause.entities)

        candidate_entities = filter(lambda entity: entity.is_maximal_regarding(candidate_entities), candidate_entities)
        # if self.debug_mode: print "2: ", candidate_entities

        candidate_chains = self.group_entities_in_chains(candidate_entities)

        candidate_chains = filter(lambda chain: not self.is_enumeration(chain), candidate_chains)

        appositions = []
        for candidate_chain in candidate_chains:
            if len(candidate_chain) > 1:
                candidate_chain.sort(key=lambda p_entity: p_entity.token.start())
                named_candidates = filter(lambda entity: "semantic_classification" in entity.msi
                                                         and entity.msi["semantic_classification"] is not None,
                                          candidate_chain)
                reference_entity = named_candidates[0] if named_candidates else candidate_chain[0]
                if all(entity.node.father == reference_entity.node.father for entity in candidate_chain) \
                   and all(e.matches(reference_entity) for e in candidate_chain):

                    entities_in_apposition = filter(lambda p_entity: p_entity is not reference_entity, candidate_chain)
                    apposition = (reference_entity, entities_in_apposition)
                    appositions.append(apposition)

        return appositions

    def is_close_to_lexical_form(self, entity, lemmas, distance):
        """Checks the presence of a lemma (from lemmas) within distance from entity.

        :param lemmas: list of lemmas to look for.
        :param distance: number of (same level) nodes between the entity and the first lexical form
        :return: bool
        """

        # print "Entering ClauseAnalyzer.is_close_to_lexical_form(entity: ", entity, ", lemmas: ", lemmas, ")"

        clause_leaves = self.clause.proper_leaves()
        leaf_positions = {leaf: index for (index, leaf) in enumerate(clause_leaves)}

        last_leaf = entity.leaves()[-1]
        idx_last_leaf = leaf_positions[last_leaf]

        is_close = last_leaf.lemma in lemmas \
                   or len(clause_leaves) > idx_last_leaf+1 and clause_leaves[idx_last_leaf+1].lemma in lemmas

        same_level_nodes = entity.node.father.children
        e_idx = same_level_nodes.index(entity.node)
        if not is_close and distance > 0 \
                        and len(same_level_nodes) > e_idx+distance+1:
            middle_are_ok = True
            for idx in range(1, distance):
                middle_node = same_level_nodes[e_idx+idx]
                middle_are_ok = middle_are_ok \
                                and self.clause.same_hemiclause(middle_node, entity.node) \
                                and not middle_node.label_lemma_matches([], ["y"])
            if middle_are_ok:
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