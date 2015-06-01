# -*- coding: utf-8 -*-
import re
import sys
import traceback

from src.rewrite.rewrite import Rewrite
from src.utils.configProvider import ConfigProvider


# TODO: in the child of the node of the closure check if the vser sabd

debug_mode = False


class VoicePassiveStrategy:

    def __init__(self, ontology):
        if debug_mode: print "--> VoicePassiveStrategy.init()"
        self.ontology = ontology
        self.persons = self._get_persons()
        self.demonyms = self._get_demonyms()

    def applies_to(self, sentence, node):
        appliance_vector = (self.applies_to_clause(clause) for clause in sentence.clauses)
        return any(appliance_vector)

    def rewrite(self, sentence, node):
        if debug_mode: print "--> VoicePassiveStrategy.rewrite(sentence: ", sentence, ", node: ", node, ")"

        clauses = []
        try:
            clauses = [[clause, sentence.clauses[idx+1]] for idx, clause in enumerate(sentence.clauses)
                       if self.applies_to_clause(clause) and idx+1 < len(sentence.clauses)]

            # check the last clause
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
        config = ConfigProvider()
        persons_filename = config.get("resources", "persons")

        for line in open(persons_filename, 'r'):
            if line[0] not in ['<', '%', '\n']:
                persons.append(line.rstrip('\n'))

        return persons

    def _get_demonyms(self):
        """
        load resource list of animated persons

        :return: list of words as list
        """
        demonyms = []
        config = ConfigProvider()
        demonyms_filename = config.get("resources", "demonyms")

        for line in open(demonyms_filename, 'r'):
            if line[0] not in ['<', '%', '\n']:
                demonyms.append(line.rstrip('\n'))

        return demonyms

    def is_animated(self, entity):
        """

        :type od: Entity
        """

        try:
            # if the entity has kernel
            if entity.kernel:
                # return if the kernel is animated or not
                return self._is_animated_single_entity(entity.kernel.lemma, entity.msi)

            # if there isn't a kernel check if there is a list of entities
            elif entity.node == 'coor-n':
                # check all the child entities
                for child in entity.children:
                    # if some of the entities are animated then return True
                    if self._is_animated_single_entity(child.kernel.lemma, child.msi):
                        return True
            else:
                child = entity.children[0]
                return self._is_animated_single_entity(child.kernel.lemma, child.msi)

        except Exception as e:
            print e.message
            ex_type, ex, tb = sys.exc_info()
            traceback.print_tb(tb)
            raise

        # other cases return False
        return False

    def _is_animated_single_entity(self, lemma, msi):
        return lemma in self.persons \
            or lemma in self.demonyms\
            or msi['semantic_classification'] == 'person'

    def rewrite_clause(self, node, sentence, clauses):
        clause = None
        ntext = ""
        try:
            clause = clauses[0][0]
            next_clause = clauses[0][1]

            # get the first leaf to extract the msi
            leaf = clause.verb.leaves()[0]

            msi = {"mode": leaf.msi["mode"],
                   "time": leaf.msi["time"],
                   "person": clause.structure('subject').msi()["person"],
                   "number": clause.structure('subject').msi()['number']}

            # transform the last leaf of verb (ie clause.verb) to the msi of the first leaf of verb
            lexical_forms = self.ontology.get_lexical_forms(clause.verb.lemma(), msi)
            rewritten_verb = filter(lambda lf: lf.text != leaf.lexical_form, lexical_forms)[0].text

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

            if clause.structure('od').entity().is_tacit() or self.is_animated(clause.structure('od').entity()) or\
            (od_msi['category'] == 'pronoun' and od_msi['type'] == 'personal'):
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
            paragraph = sentence.paragraph.text.decode("utf-8")
            start = clause.proper_leaves()[0].token.start()

            if start > 0:
                if start > 2:
                    if paragraph[start-2:start].strip(' ') in ['"', ':', '.', '-']:
                        ntext = ntext[0].upper() + ntext[1:]
            elif start == 0:
                ntext = ntext[0].upper() + ntext[1:]

            ntext = ntext.replace('_', ' ').strip()

        except Exception as e:
            print e.message
            ex_type, ex, tb = sys.exc_info()
            traceback.print_tb(tb)
            ex_type, ex, tb = sys.exc_info()
            logger = get_logger('tecnonews')
            logger.info("VoicePassiveStrategy Rewriting:")
            logger.info(e.message)
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
