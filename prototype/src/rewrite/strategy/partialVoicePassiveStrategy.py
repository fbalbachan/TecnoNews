#-*- coding: utf-8 -*-
from src.rewrite.rewrite import Rewrite
from src.utils.configProvider import ConfigProvider
from src.utils.collectionUtils import dict_by
from src.utils.stringUtils import set_first_letter_case
from src.model.entity.tacitEntity import TacitEntity
from src.utils.logger_utils import *


import ConfigParser
import re
import sys, traceback

# TODO: in the child of the node of the closure check if the vser sabd


class PartialVoicePassiveStrategy:
    def __init__(self, ontology):
        self.ontology = ontology
        self.persons = self._get_persons()
        self.demonyms = self._get_demonyms()

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
        return self.is_partial(clause) and clause.voice == 'passive' and \
               clause.verb and clause.verb.transitivity == 'TRANSITIVE' and\
               clause.node.label == "verb-pass"

    def is_partial(self, clause):
        return clause.has_structure('od') and not clause.structure('od').is_tacit() and \
               clause.has_structure('subject') and clause.structure('subject').entity().has_attr("implicit") and\
               not self.is_animated(clause.structure('od').entity())

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
        try:
            clause = clauses[0][0]
            next_clause = clauses[0][1]

            # get the first leaf to extract the msi
            leaf = clause.verb.leaves()[0]

            msi = {"mode": leaf.msi["mode"], "time": leaf.msi["time"], "person": 3,
                   "number": clause.structure('od').msi()['number']}
            # print "leaf.lemma", leaf.lemma

            # transform the last leaf of verb (ie clause.verb) to the msi of the first leaf of verb
            lexical_forms = self.ontology.get_lexical_forms(clause.verb.lemma(), msi)
            rewrited_verb = filter(lambda lf: lf.text != leaf.lexical_form, lexical_forms)[0].text
            # print "rewrited_verb", rewrited_verb

            text = clause.node.leaves_string()
            verb = clause.structure('verb').lexical_form()

            od = clause.structure('od').lexical_form()
            od_rewritten = od


            # lower case od if is not a proper name
            od_msi = clause.structure('od').entity().msi
            if not self.is_proper_name(od_msi):
                od_rewritten = od[0].lower() + od[1:]

            if next_clause and next_clause.relative_entity == clause.structure('od').entity():
                od_rewritten = od_rewritten + " " + next_clause.__repr__().strip()
                print od_rewritten
                repls = (verb, ''), (od, ''), ( " " + next_clause.__repr__(), '')
            else:
                repls = (verb, ''), (od, '')

            ntext = self.multiple_replace(text, *repls).strip(' ')
            ntext = ntext[0].lower() + ntext[1:]

            ntext = "se " + rewrited_verb + " " + od_rewritten +  " " + ntext
            ntext = ntext.replace(' ,', ',')
            # Fix space with point at the end
            if ntext[-2:] == ' .':
                ntext = ntext[:-2] + '.'

            paragraph = sentence.paragraph.text.decode("utf-8")
            start = clause.proper_leaves()[0].token.start()

            if start > 0:
                if start > 2:
                    if paragraph[start-2:start].strip(' ') in ['"', ':', '.', '-']:
                        ntext = ntext[0].upper() + ntext[1:]
            elif start == 0:
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
