# -*- coding: utf-8 -*-
from src.ling.gender import Gender

__author__ = 'Martín Caramés Abente'

import traceback
import re

from src.rewrite.rewrite import Rewrite
from src.utils.logger_utils import *
from src.utils.stringUtils import *

debug_mode = False


class SeImpersonalStrategy:
    def __init__(self, ontology):
        if debug_mode: print "--> SeImpersonalStrategy.init()"
        self.ontology = ontology

    def applies_to(self, sentence, node):
        if debug_mode: print "--> SeImpersonalStrategy.applies_to(sentence:", sentence.text, ")"

        result = False
        for sentence_clause in sentence.clauses:
            if sentence_clause.node == node:
                result = self.applies_to_clause(sentence_clause)
                break

        return result

    def applies_to_clause(self, clause):
        if debug_mode: print "--> SeImpersonalStrategy.applies_to_clause(", clause.node, ")"

        subject_entity = clause.structure('subject').entity()
        result = not clause.is_relative() and "impersonal" in subject_entity.attributes.keys()
        return result

    def rewrite(self, sentence, node):
        if debug_mode: print "--> SeImpersonalStrategy.rewrite(sentence:", sentence, ", node:", node, ")"

        rewrite = None
        try:
            for sentence_clause in sentence.clauses:
                if sentence_clause.node == node:
                    rewrite = self.rewrite_clause(sentence, sentence_clause)
                    break

        except Exception as e:
            logger = get_logger('tecnonews')
            logger.info("SeImpersonalStrategy Rewrite exception: ")
            logger.info((": " + e.message) if e and hasattr(e, "message") else "")
            ex_type, ex, tb = sys.exc_info()
            logger.info(traceback.format_tb(tb))

        if debug_mode: print "<-- SeImpersonalStrategy.rewrite()"
        return rewrite

    def rewrite_clause(self, sentence, clause):
        if debug_mode: print "--> SeImpersonalStrategy.rewrite_clause(clause:", clause, ")\n"

        replacement_string = self.get_clause_replacement_string(sentence, clause)
        rewrite_rule = Rewrite.preserving_case(clause.node, replacement_string)

        if debug_mode: print "<-- SeImpersonalStrategy.rewrite_clause()\n"
        return rewrite_rule

    def get_clause_replacement_string(self, sentence, clause):
        if debug_mode: print "--> SeImpersonalStrategy.get_clause_replacement_string(clause:", clause, ")\n"

        rewritten_verb = self.flex_verb(clause)

        beginning_text, ending_text = self.trim_known_elements(clause)

        od_string = str(clause.structure('od').entity())

        header = clause.is_subordinated_clause()

        new_clause_text = ""
        if len(beginning_text) > 0:
            new_clause_text = (header.lexical_form + " " if header else "") + beginning_text
            new_clause_text = set_first_letter_case(clause.node.leaves()[0].lexical_form, new_clause_text).rstrip()

        elif header:
            new_clause_text = header.lexical_form

        new_clause_text += " " if len(new_clause_text) > 0 else ""
        new_clause_text += od_string + " " + rewritten_verb

        if len(beginning_text) == 0 and not header and od_string[0].islower():
            new_clause_text = set_first_letter_case(clause.node.leaves()[0].lexical_form, new_clause_text).rstrip()

        if len(ending_text) > 0:
            new_clause_text += (" " if len(ending_text) > 1 else "")
            new_clause_text += ending_text

        new_clause_text = new_clause_text.replace('_', ' ').rstrip()

        if debug_mode: print "<-- SeImpersonalStrategy.get_clause_replacement_string() --> new_clause_text: ", new_clause_text, "\n"
        return new_clause_text

    def trim_known_elements(self, clause):
        if debug_mode: print "--> SeImpersonalStrategy.trim_known_elements(clause:", clause, ")"

        od_string = clause.structure('od').lexical_form().replace("_", " ")
        replacements = [("A " + od_string, ""), ("a " + od_string, ""), (od_string, "")]

        left_hemiclause_leaves, right_hemiclause_leaves = clause.get_hemiclauses()
        if debug_mode:
            print "left_hemiclause_leaves: ", left_hemiclause_leaves
            print "right_hemiclause_leaves: ", right_hemiclause_leaves

        # The method get_hemiclauses() will NOT ALWAYS return the header,
        # so we remove it here and add it later, by hand
        header = clause.is_subordinated_clause()
        if header:
            header_orig_node = clause.original_by_proper(header)
            if header_orig_node in left_hemiclause_leaves:
                left_hemiclause_leaves.remove(header_orig_node)
            if header_orig_node in right_hemiclause_leaves:
                right_hemiclause_leaves.remove(header_orig_node)

        beginning = ""
        for leaf in left_hemiclause_leaves:
            if leaf.msi["category"] != "punctuation":
                beginning += " "
            beginning += leaf.joined_text()

        beginning = self.multiple_replace(beginning, *replacements).strip()
        if len(beginning) >= 2 and beginning[-2:].lower() == "se":
            beginning = beginning[:-3].strip()
        if clause.is_negated():
            if len(beginning) >= 2 and beginning[-2:].lower() == "no":
                beginning = beginning[:-3].strip()

        ending = ""
        for leaf in right_hemiclause_leaves:
            if leaf.msi["category"] != "punctuation":
                ending += " "
            ending += leaf.joined_text()
        ending = self.multiple_replace(ending, *replacements).strip()

        if debug_mode: print "<-- trim_known_elements() --> beginning: ", beginning, " - ending: ", ending
        return beginning, ending

    def flex_verb(self, clause):
        if debug_mode: print "--> SeImpersonalStrategy.flex_verb(clause:", clause, ")\n"
        od_entity = clause.structure('od')
        verb = clause.verb
        has_compound_time = verb.has_compound_time()
        leaves = verb.node.leaves()
        nr_leaves = len(leaves)

        if leaves[-1].msi["mode"] != "infinitive":
            flexed_aux_verb = self.flex_auxiliary_verb(verb, od_entity)
            flexed_participle = self.flex_verb_participle(verb, od_entity)
            flexed_verb = flexed_aux_verb + " " + flexed_participle

        # 2) verb + infinitive  --  List of verbs: intentar, deber, poder, soler
        elif (not has_compound_time and nr_leaves == 2 or has_compound_time and nr_leaves == 3) \
              and leaves[-2].lemma in ["intentar", "deber", "poder", "soler"]:

            flexed_participle = self.flex_verb_participle(verb, od_entity)
            flexed_modal_verb = self.flex_modal_verb(verb, od_entity)
            flexed_verb = flexed_modal_verb + " " + "ser" + " " + flexed_participle

        elif (not has_compound_time and nr_leaves == 3 or has_compound_time and nr_leaves == 4) \
              and self.is_verb_from_third_group(verb):
            flexed_participle = self.flex_verb_participle(verb, od_entity)
            flexed_modal_verb = self.flex_modal_verb(verb, od_entity)
            flexed_verb = flexed_modal_verb + " " + leaves[-2].lexical_form + " " + "ser" + " " + flexed_participle

        else:
            raise Exception("Invalid verb found: " + str(clause.verb))

        if clause.is_negated():
            flexed_verb = "no " + flexed_verb

        if debug_mode: print "<-- SeImpersonalStrategy.flex_verb() --> flexed_verb: ", flexed_verb, "\n"
        return flexed_verb

    def flex_auxiliary_verb(self, verb, od_entity):
        if debug_mode: print "--> SeImpersonalStrategy.flex_auxiliary_verb(verb:", verb, " - od_entity: ", od_entity, ")\n"
        leaf = verb.node.leaves()[0]
        aux_msi = {"mode": leaf.msi["mode"],
                   "time": leaf.msi["time"],
                   "person": leaf.msi["person"],
                   #"number": od_entity.number()
                   "number": od_entity.msi()['number']}

        lexical_forms = self.ontology.get_lexical_forms("ser", aux_msi)
        aux_verb_flexed = lexical_forms[0].text
        return aux_verb_flexed

    def flex_modal_verb(self, verb, od_entity):
        msi = verb.node.leaves()[0].msi
        modal_msi = {"mode": msi["mode"],
                     "time": msi["time"],
                     "person": msi["person"],
                     #"number": od_entity.number()
                     "number": od_entity.msi()['number']}

        if not verb.has_compound_time():
            lemma = verb.node.leaves()[0].lemma
        else:
            lemma = verb.node.leaves()[1].lemma
        lexical_forms = self.ontology.get_lexical_forms(lemma, modal_msi)

        modal_verb_flexed = lexical_forms[0].text
        return modal_verb_flexed

    def flex_verb_participle(self, verb, od_entity):
        if debug_mode: print "--> SeImpersonalStrategy.flex_verb_participle(verb:", verb, " - od_entity: ", od_entity, ")\n"

        #gender = od_entity.gender()
        gender = od_entity.msi()['gender']
        gender = gender if gender is not Gender.neutral else Gender.masculine

        participle_msi = {"mode":   "participio",
                          "gender": gender,
                          #"number": od_entity.number()
                          "number": od_entity.msi()['number']}

        lexical_forms = self.ontology.get_lexical_forms(verb.lemma(), participle_msi)
        clause_verb_participle = lexical_forms[0].text
        return clause_verb_participle

    def is_verb_from_third_group(self, verb):
        # 3) example: tener   + que + infinitive  -- List: ,,,,
        #    example: empezar + a   + infinitive  -- List: ,,,
        #    example: acabar  + de  + infinitive  -- List: ,,,
        #    example: tardar  + en  + infinitive  -- List: ,,,,
        leaves = verb.node.leaves()

        it_is_from_group_a = leaves[-2].lemma == "que" and leaves[-3].lemma == "tener"

        it_is_from_group_b = leaves[-2].lemma == "a" \
                             and leaves[-3].lemma in ["ir", "venir", "empezar", "comenzar", "echarse", "acertar",
                                                      "volver", "echar", "llegar", "romper", "acostumbrar", "alcanzar"]

        it_is_from_group_c = leaves[-2].lemma == "de" \
                             and leaves[-3].lemma in ["haber", "deber", "acabar", "terminar", "dejar"]

        it_is_from_group_d = leaves[-2].lemma == "en" and leaves[-3].lemma == "tardar"

        return it_is_from_group_a or it_is_from_group_b or it_is_from_group_c or it_is_from_group_d

    def multiple_replacer(self, *key_values):
        replace_dict = dict(key_values)
        replacement_function = lambda match: replace_dict[match.group(0)]
        pattern = re.compile("|".join([re.escape(k) for k, v in key_values]), re.M)
        return lambda string: pattern.sub(replacement_function, string)

    def multiple_replace(self, string, *key_values):
        return self.multiple_replacer(*key_values)(string)

    type = "dislocation"
