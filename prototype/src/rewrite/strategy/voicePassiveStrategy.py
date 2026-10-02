# -*- coding: utf-8 -*-
import re
import sys
import traceback

from src.rewrite.rewrite import Rewrite
from src.utils.configProvider import ConfigProvider
from src.utils.logger_utils import get_logger
from src.model.entity.animity import Animity


# TODO: in the child of the node of the closure check if the vser sabd


debug_mode = False
logger = get_logger('tecnonews')


class VoicePassiveStrategy:

    def __init__(self, ontology):
        if debug_mode: print("--> VoicePassiveStrategy.init()")
        self.ontology = ontology

    def applies_to(self, sentence, node):
        if debug_mode: print("--> VoicePassiveStrategy.applies_to(sentence: ", sentence, ")")
        appliance_vector = (self.applies_to_clause(clause) for clause in sentence.clauses)
        applies = any(appliance_vector)

        if debug_mode: print("<-- VoicePassiveStrategy.applies_to = ", str(applies))
        return applies

    def rewrite(self, sentence, node):
        if debug_mode: print("--> VoicePassiveStrategy.rewrite(sentence: ", sentence, ", node: ", node, ")")

        rewrite_rule = None

        try:
            clauses = [[clause, sentence.clauses[idx+1]] for idx, clause in enumerate(sentence.clauses)
                       if self.applies_to_clause(clause) and idx+1 < len(sentence.clauses)]

            # check the last clause
            last_clause = sentence.clauses[-1]
            if self.applies_to_clause(last_clause):
                clauses.append([last_clause, None])

            rewrite_rule = self.rewrite_clause(node, sentence, clauses)

        except Exception as e:
            logger = get_logger('tecnonews')
            logger.info("VoicePassiveStrategy Rewrite exception:")
            logger.info(str(e))
            ex_type, ex, tb = sys.exc_info()
            logger.info(traceback.format_tb(tb))

        return rewrite_rule

    def applies_to_clause(self, clause):
        if debug_mode: print("--> VoicePassiveStrategy.applies_to_clause(clause: ", clause, ")")

        applies = self.is_complete(clause) \
                  and clause.voice == 'passive' \
                  and clause.verb and clause.verb.transitivity == 'TRANSITIVE' \
                  and clause.node.label == "verb-pass"

        if debug_mode: print("<-- VoicePassiveStrategy.applies_to_clause = ", str(applies))
        return applies

    def is_complete(self, clause):
        if debug_mode: print("--> VoicePassiveStrategy.is_complete(clause: ", clause, ")")

        is_complete = clause.has_structure('subject') \
                      and not clause.structure('subject').is_tacit() \
                      and clause.has_structure('od') \
                      and (not clause.structure('od').is_tacit()
                           or (clause.structure('od').is_tacit()
                               and clause.structure('od').entity().coref_chain != []))

        if debug_mode: print("<-- is_complete? ", str(is_complete))
        return is_complete

    def rewrite_clause(self, node, sentence, clauses):
        clause = None
        ntext = ""
        try:
            clause = clauses[0][0]
            next_clause = clauses[0][1]

            # get the first leaf to extract the msi
            leaf = clause.verb.leaves()[0]

            #print clause.structure('subject')
            #print clause.structure('subject').msi()

            msi = {"mode": leaf.msi["mode"],
                   "time": leaf.msi["time"],
                   "person": clause.structure('subject').msi()['person'],
                   "number": clause.structure('subject').msi()['number']}

            # transform the last leaf of verb (ie clause.verb) to the msi of the first leaf of verb
            lexical_forms = self.ontology.get_lexical_forms(clause.verb.lemma(), msi)
            rewritten_verb = [lf for lf in lexical_forms if lf.text != leaf.lexical_form][0].text

            text = clause.node.leaves_string()
            verb = clause.structure('verb').lexical_form()

            if clause.structure('od').is_tacit():
                od = clause.structure('od').entity().referenced().lexical_form
            else:
                od = clause.structure('od').lexical_form()

            subject = clause.structure('subject').lexical_form()
            od = clause.structure('od').lexical_form()

            subject_rewritten = subject
            od_rewritten = od

            subject_pattern = "por " + subject

            # lower case od if is not a proper name
            od_msi = clause.structure('od').entity().msi
            if not self.is_proper_name(od_msi):
                od_rewritten = od[0].lower() + od[1:]

            if clause.structure('od').entity() and not clause.structure('od').is_tacit():
                od_msi = clause.structure('od').all_entities()[0].leaves()[0].msi

            od_entity = clause.structure('od').entity()
            od_matches_animated = Animity.animities_match(od_entity.msi["animity"], Animity.animated)
            if clause.structure('od').entity().is_tacit() \
               or od_matches_animated \
               or (od_msi['category'] == 'pronoun' and od_msi['type'] == 'personal'):

                if od_rewritten[0:3] == 'el ':
                    od_rewritten = 'al ' + od_rewritten[3:]
                elif od_rewritten[0:3] == 'yo ' or od_rewritten[0:3] == 'yo':
                    od_rewritten = 'a mí'
                else:
                    od_rewritten = 'a ' + od_rewritten

            if next_clause and next_clause.relative_entity == clause.structure('subject').entity():
                subject_rewritten = subject_rewritten + " " + next_clause.__repr__().strip()
                repls = (verb, rewritten_verb), \
                        (subject_pattern, od_rewritten), \
                        (od, subject_rewritten), \
                        (next_clause.__repr__(), '')

            elif next_clause and next_clause.relative_entity == clause.structure('od').entity():
                od_rewritten = od_rewritten + " " + next_clause.__repr__().strip()
                repls = (verb, rewritten_verb), \
                        (subject_pattern, od_rewritten), \
                        (od, subject_rewritten), \
                        (" " + next_clause.__repr__(), '')

            else:
                repls = (verb, rewritten_verb), \
                        (subject_pattern, od_rewritten), \
                        (od, subject_rewritten)

            ntext = self.multiple_replace(text, *repls)

            # If OD is tacit
            if clause.structure('od').is_tacit():
                ntext = subject_rewritten + " " + ntext

            # Fix space with point at the end
            if ntext[-2:] == ' .':
                ntext = ntext[:-2] + '.'

            # Uppercase if produced text if the start of a sentence
            paragraph = sentence.paragraph.text
            start = clause.proper_leaves()[0].token.start()

            if start > 0:
                if start > 2:
                    if paragraph[start-2:start].strip(' ') in ['"', ':', '.', '-']:
                        ntext = ntext[0].upper() + ntext[1:]
            elif start == 0:
                ntext = ntext[0].upper() + ntext[1:]

            ntext = ntext.replace('_', ' ').strip()

        except Exception as e:
            ex_type, ex, tb = sys.exc_info()
            logger.info("VoicePassiveStrategy Rewriting:")
            logger.info(str(e))
            logger.info(traceback.print_tb(tb))

        return Rewrite(clause.node, ntext)

    def is_proper_name(self, msi):
        return not (msi['category'] != 'noun' or (
                msi['category'] == 'noun' and
                            msi['semantic_classification'] is None))

    def multiple_replacer(self, *key_values):
        replace_dict = dict(key_values)
        replacement_function = lambda match: replace_dict[match.group(0)]
        pattern = re.compile("|".join([re.escape(k) for k, v in key_values]), re.M)
        return lambda string: pattern.sub(replacement_function, string)

    def multiple_replace(self, string, *key_values):
        return self.multiple_replacer(*key_values)(string)

    type = "dislocation"
