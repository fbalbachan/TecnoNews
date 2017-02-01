# -*- coding: utf-8 -*-
import csv
import re

from src.utils.configProvider import ConfigProvider
from src.rewrite.rewrite import Rewrite


# from src.utils.stringUtils import set_first_letter_case


debug_mode = False


class SynonymsStrategy:

    def __init__(self, ontology):
        if debug_mode: print "--> SynonymsStrategy.__init__()"
        self.ontology = ontology
        self.synonyms = self._get_synonyms()
        self.adverbs = self._get_adverbs()
        self.locutions = self._get_locutions()
        self.unidirectional_synonyms = self._get_unidirectional_synonyms()
        self.synonyms.update(self.unidirectional_synonyms)

    def applies_to(self, clause):
        for leaf in clause.proper_leaves():
            if (leaf.lemma in self.synonyms.keys()
               or leaf.lexical_form in self.adverbs.keys()):
                return True
        return False

    def rewrite(self, clause):
        if debug_mode: print "--> SynonymsStrategy.rewrite(clause: ", clause, ")"
        ontology = self.ontology

        rewrites = []
        for leaf in clause.proper_leaves():
            replacement = None

            if 'semantic_classification' in leaf.msi and leaf.msi['semantic_classification'] != None:
                continue

            if leaf.lemma in self.synonyms.keys():
                synonym = self.synonyms[leaf.lemma]
                if '_' in synonym or synonym not in ontology.concepts:
                    if synonym in self.locutions and self.locutions[synonym]:
                        pass
                    replacement = synonym.replace('_', ' ')
                else:
                    concept = ontology.concept(synonym)
                    leaf_msi = self._msi_transform(leaf.msi)
                    lexical_forms = [form for form in concept.lexical_forms if leaf_msi == self._msi_transform(form.msi)]
                    if lexical_forms:
                        if leaf.msi['category'] == 'noun' and 'gender' in leaf.msi and leaf.msi['gender'] != 'neutral':
                            if len(lexical_forms) > 1 and 'gender' in lexical_forms[0].msi and leaf.msi['gender'] != lexical_forms[0].msi['gender']:
                                rewrites += self.rewrite_entity(clause, leaf, lexical_forms[1], ontology)
                            else:
                                rewrites += self.rewrite_entity(clause, leaf, lexical_forms[0], ontology)
                        #if leaf.msi['category'] == 'noun' and 'gender' in leaf.msi and 'gender' in lexical_forms[0].msi and leaf.msi['gender'] != 'neutral' and leaf.msi['gender'] != lexical_forms[0].msi['gender']:
                        #    rewrites += self.rewrite_entity(clause, leaf, lexical_forms[0], ontology)
                        else:
                            replacement = lexical_forms[0].text

                if replacement:
                    rewrites.append(Rewrite.preserving_case(leaf, replacement))

            if not replacement and leaf.lexical_form in self.adverbs.keys():
                adverb = self.adverbs[leaf.lexical_form]
                rewrites.append(Rewrite.preserving_case(leaf, adverb.replace('_', ' ')))

        return rewrites


    def rewrite_entity(self, clause, leaf, target_synonym, ontology):
        target_gender = target_synonym.msi['gender']
        found_entity = None
        for an_entity in clause.entities:

            if str(an_entity.kernel) == str(leaf.lexical_form):
                found_entity = an_entity
                break

        rewrites = [Rewrite.preserving_case(leaf, target_synonym.text)]
        #Solo cambio el resto de la entidad si el genero NO es neutro!
        if found_entity != None and target_gender != u'neutral':

            #SKIP WORDS CONTAINED IN NESTED ENTITIES ("muro de usuarios" -> "pared de USUARIAS"!!)
            #kernel_leaf_level = leaf.level()

            #nested = found_entity.get_nested_entities()
            #nested_leaves = []
            #for a_nested in nested:
            #    nested_leaves.extend([a_leaf.lexical_form for a_leaf in a_nested.leaves()])

            nested_entities = found_entity.get_nested_entities()
            current_tree = found_entity.node
            for a_subord_entity in nested_entities:
                current_tree = current_tree.cloned_by_original(a_subord_entity.node)
                break

            for a_leaf in [a_node for a_node in current_tree if a_node.is_leaf()]:

                #SKIPS!
                #if a_leaf.lexical_form in nested_leaves:
                #    continue
                #if a_leaf.level() != kernel_leaf_level:
                #    continue

                leaf_msi = self._msi_transform(a_leaf.msi)
                leaf_msi['gender'] = target_gender
                if a_leaf != leaf and 'gender' in a_leaf.msi and a_leaf.msi['gender'] != target_gender and a_leaf.msi['gender'] != 'neutral' and a_leaf.lemma in ontology.concepts:
                    lexical_forms = ontology.concept(a_leaf.lemma).lexical_forms
                    for a_form in lexical_forms:
                        form_msi = self._msi_transform(a_form.msi)
                        if 'gender' not in form_msi:
                            continue
                        form_msi['gender'] = a_form.msi['gender']
                        #print "MSI COMPARE"
                        #print form_msi
                        #print leaf_msi
                        if form_msi == leaf_msi:
                        #if 'gender' in a_form.msi and a_form.msi['gender'] == target_gender:
                            rewrites.append(Rewrite.preserving_case(a_leaf, a_form.text))

        return rewrites



    def _get_synonyms(self):
        if debug_mode: print "--> SynonymsStrategy._get_synonyms()"
        return self._get_replacements_from_csv("synonyms")

    def _get_adverbs(self):
        return self._get_replacements_from_csv("adverb_forms")

    def _get_unidirectional_synonyms(self):
        if debug_mode: print "--> SynonymsStrategy,_get_unidirectional_synonyms()"
        return self._get_single_replacements_from_csv("unidirectional_synonyms")

    def _get_replacements_from_csv(self, resource):
        if debug_mode: print "--> SynonymsStrategy._get_replacements_from_csv()"
        # Warning, it is a dict, it doesn't work for multiple replacements for the same word.

        replacements = {}
        config = ConfigProvider()
        replacements_filename = config.get("resources", resource)
        for line in csv.reader(open(replacements_filename, 'r')):
            replacements[line[0]] = line[1]
            replacements[line[1]] = line[0]
        return replacements


    def _get_single_replacements_from_csv(self, resource):
        replacements = {}
        config = ConfigProvider()
        replacements_filename = config.get("resources", resource)
        for line in csv.reader(open(replacements_filename, 'r')):
            replacements[line[0]] = line[1]
        return replacements

    def _get_locutions(self):
        locutions = {}
        config = ConfigProvider()
        locutions_filename = config.get("resources", "locutions")
        regex = re.compile('<.[^_]+>')
        for line in open(locutions_filename, 'r'):
            line = line.strip().split()
            locutions[line[1]] = [y[1:-1] for y in regex.findall(line[0])]
        return locutions

    def _msi_transform(self, msi):
        if debug_mode: print "--> SynonymsStrategy._msi_transform(msi: ", msi, ")"

        result_msi = {}
        if 'number' in msi:
            result_msi['number'] = msi['number']
        if msi['category'] != 'noun':
            if 'gender' in msi:
                result_msi['gender'] = msi['gender']

        if msi['category'] == 'adjective':
            if 'grade' in msi:
                result_msi['grade'] = msi['grade']
        elif msi['category'] == 'verb':
            if 'mode' in msi:
                result_msi['mode'] = msi['mode']
            if 'person' in msi:
                result_msi['person'] = msi['person']
            if 'time' in msi:
                result_msi['time'] = msi['time']
        result_msi['category'] = msi['category']
        return result_msi

    type = "replacement"
