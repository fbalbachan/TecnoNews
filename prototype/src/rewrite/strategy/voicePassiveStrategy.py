#-*- coding: utf-8 -*-
from src.rewrite.rewrite import Rewrite
from src.utils.collectionUtils import dict_by
from src.utils.stringUtils import set_first_letter_case
from src.model.entity.tacitEntity import TacitEntity
from src.utils.logger_utils import *


import ConfigParser
import re
import sys, traceback

# TODO: in the child of the node of the closure check if the vser sabd


class VoicePassiveStrategy:
    def __init__(self, ontology):
        self.ontology = ontology
        self.persons = self._get_persons()
        self.demonym = self._get_demonym()

    def applies_to(self, sentence, node):
        return any(( self.applies_to_clause(clause) for clause in sentence.clauses))

    def rewrite(self, sentence, node):
        try:
            clauses = [[clause, sentence.clauses[idx+1]] for idx, clause in enumerate(sentence.clauses)
                       if self.applies_to_clause(clause) and idx+1 < len(sentence.clauses)]

            #check the last clause
            last_clause = sentence.clauses[-1]
            if self.applies_to_clause(last_clause):
                clauses.append([last_clause, None])
        except Exception as e:
            logger = get_logger('tecnonews')
            logger.info("VoicePassiveStrategy Rewriting:")
            logger.info(e.message)
            ex_type, ex, tb = sys.exc_info()
            logger.info(traceback.format_tb(tb))
        return self.rewrite_clause(node, sentence, clauses)

    def applies_to_clause(self, clause):
        return self.is_complete(clause) and clause.voice == 'passive' and \
               clause.verb and clause.verb.transitivity == 'TRANSITIVE' and\
               clause.node.label == "verb-pass"

    def is_complete(self, clause):
        return clause.has_structure('subject') and not clause.structure('subject').is_tacit() and \
               clause.has_structure('od') and (not clause.structure('od').is_tacit() or
                                               (clause.structure('od').is_tacit() and
                                                clause.structure('od').entity().coref_chain != []))

    def _get_persons(self):
        """
        load resource list of animated persons

        :return: list of words as list
        """
        persons = []
        config = ConfigParser.ConfigParser()
        config.read("config")
        persons_filename = config.get("resources", "persons")

        for line in open(persons_filename, 'r'):
            if line[0] not in ['<', '%', '\n']:
                persons.append(line.rstrip('\n'))

        return persons

    def _get_demonym(self):
        """
        load resource list of animated persons

        :return: list of words as list
        """
        demonym = []
        config = ConfigParser.ConfigParser()
        config.read("config")
        demonym_filename = config.get("resources", "demonym")

        for line in open(demonym_filename, 'r'):
            if line[0] not in ['<', '%', '\n']:
                demonym.append(line.rstrip('\n'))

        return demonym

    def is_animated(self, od):
        """

        :type od: Entity
        """
        if od.is_tacit():
            return True
        else:
            if od.kernel.lemma in self.persons \
                    or od.kernel.lemma in self.demonym\
                    or od.msi['semantic_classification'] == 'person':
                return True

        return False

    def rewrite_clause(self, node, sentence, clauses):
        try:
            clause = clauses[0][0]
            next_clause = clauses[0][1]
            print clauses

            # get the first leaf to extract the msi
            leaf = clause.verb.leaves()[0]

            msi = {"mode": leaf.msi["mode"], "time": leaf.msi["time"], "person": clause.structure('subject').msi()["person"],
                   "number": clause.structure('subject').msi()['number']}
            # print "leaf.lemma", leaf.lemma

            # transform the last leaf of verb (ie clause.verb) to the msi of the first leaf of verb
            lexical_forms = self.ontology.get_lexical_forms(clause.verb.lemma(), msi)
            rewrited_verb = filter(lambda lf: lf.text != leaf.lexical_form, lexical_forms)[0].text
            # print "rewrited_verb", rewrited_verb

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

            if self.is_animated(clause.structure('od').entity()) or\
            (od_msi['category'] == 'pronoun' and od_msi['type'] == 'personal'):
                if od_rewritten[0:3] == 'el ':
                    od_rewritten = 'al ' + od_rewritten[3:]
                elif od_rewritten[0:3] == 'yo ' or od_rewritten[0:3] == 'yo':
                    od_rewritten = 'a mí'
                else:
                    od_rewritten = 'a ' + od_rewritten

            if next_clause and next_clause.relative_entity == clause.structure('subject').entity():
                subject_rewritten = subject_rewritten + " " + next_clause.__repr__().strip()
                repls = (verb, rewrited_verb), (subject_pattern, od_rewritten), (od, subject_rewritten), (next_clause.__repr__(), '')
            elif next_clause and next_clause.relative_entity == clause.structure('od').entity():
                od_rewritten = od_rewritten + " " + next_clause.__repr__().strip()
                repls = (verb, rewrited_verb), (subject_pattern, od_rewritten), (od, subject_rewritten), ( " " + next_clause.__repr__(), '')
            else:
                repls = (verb, rewrited_verb), (subject_pattern, od_rewritten), (od, subject_rewritten)

            ntext = self.multiple_replace(text, *repls)

            # If OD is tacit
            if clause.structure('od').is_tacit():
                ntext = subject_rewritten + " " + ntext

            # Fix space with point at the end
            if ntext[-2:] == ' .':
                ntext = ntext[:-2] + '.'

            if sentence.paragraph.text[0:10] == text[0:10]:
                ntext = ntext[0].upper() + ntext[1:]

        except Exception as e:
            ex_type, ex, tb = sys.exc_info()
            traceback.print_tb(tb)
            ex_type, ex, tb = sys.exc_info()
            logger = get_logger('tecnonews')
            logger.info("VoicePassiveStrategy Rewriting:")
            logger.info(e.message)
            logger.info(traceback.print_tb(tb))
        return Rewrite(clause.node, ntext.replace('_', ' ').strip())


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
