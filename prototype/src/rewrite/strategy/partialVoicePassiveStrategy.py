# -*- coding: utf-8 -*-
import re
import sys
import traceback

from src.rewrite.rewrite import Rewrite
from src.utils.logger_utils import get_logger
from src.model.entity.animity import Animity
from src.ling.number import Number


# TODO: in the child of the node of the closure check if the vser sabd
debug_mode = False


logger = get_logger('tecnonews')


class PartialVoicePassiveStrategy:
    def __init__(self, ontology):
        self.ontology = ontology

    def applies_to(self, sentence, node):
        if debug_mode: print "--> PartialVoicePassiveStrategy.applies_to(sentence: ", sentence, ")"

        applies = any((self.applies_to_clause(clause) for clause in sentence.clauses))

        if debug_mode: print "<-- applies_to: applies = ", str(applies)
        return applies

    def rewrite(self, sentence, node):
        if debug_mode: print "--> PartialVoicePassiveStrategy.rewrite(sentence: ", sentence, ")"

        clauses = []
        try:
            clauses = [[clause, sentence.clauses[idx+1]] for idx, clause in enumerate(sentence.clauses)
                       if self.applies_to_clause(clause) and idx+1 < len(sentence.clauses)]

            # Check the last clause
            last_clause = sentence.clauses[-1]
            if self.applies_to_clause(last_clause):
                clauses.append([last_clause, None])

        except Exception as e:
            logger = get_logger('tecnonews')
            logger.info("PartialVoicePassiveStrategy Rewriting exception:")
            logger.info(e.message)
            ex_type, ex, tb = sys.exc_info()
            logger.info(traceback.format_tb(tb))

        return self.rewrite_clause(node, sentence, clauses)

    def applies_to_clause(self, clause):
        if debug_mode: print "--> PartialVoicePassiveStrategy.applies_to_clause(clause: ", clause, ")"

        applies = self.is_partial(clause) and clause.voice == 'passive' and \
                  clause.verb and clause.verb.transitivity == 'TRANSITIVE' and\
                  clause.node.label == "verb-pass"

        if debug_mode: print "<-- applies_to_clause: applies = ", str(applies)
        return applies

    def is_partial(self, clause):
        if debug_mode: print "--> PartialVoicePassiveStrategy.is_partial(clause: ", clause, ")"

        has_od_and_subject = clause.has_structure('od') and clause.has_structure('subject')

        is_partial = has_od_and_subject \
               	     and clause.structure('subject').entity().has_attr("implicit") \
                     and (not clause.structure('od').is_tacit() or clause.structure('od').entity().coref_chain != [])

        if debug_mode: print "<-- PartialVoicePassiveStrategy.is_partial = ", str(is_partial)
        return is_partial

    def rewrite_clause(self, node, sentence, clauses):
        if debug_mode: print "--> PartialVoicePassiveStrategy.rewrite_clause(clauses: )"

        rewrite_rule = None
        clause = clauses[0][0]

        try:
            next_clause = clauses[0][1]
            od_entity = clause.structure('od').entity()

            if od_entity.msi["animity"] == Animity.inanimate:
                ntext = self.rewrite_clause_od_inanimate(node, sentence, clause, next_clause)
            else:
                ntext = self.rewrite_clause_od_animated(node, sentence, clause, next_clause)

            rewrite_rule = Rewrite(clause.node, ntext)

        except Exception as e:
            ex_type, ex, tb = sys.exc_info()
            logger.info("PartialVoicePassiveStrategy Rewrite_clause exception")
            logger.info(e.message)
            logger.info(traceback.print_tb(tb))

        return rewrite_rule

    def rewrite_clause_od_inanimate(self, node, sentence, clause, next_clause):
        # get the first leaf to extract the msi
        leaf = clause.verb.leaves()[0]
        od_structure = clause.structure('od')

        msi = {"mode": leaf.msi["mode"],
               "time": leaf.msi["time"],
               "person": 3,
               "number": od_structure.number()}

        # transform the last leaf of verb (ie clause.verb) to the msi of the first leaf of verb
        lexical_forms = self.ontology.get_lexical_forms(clause.verb.lemma(), msi)
        rewritten_verb = lexical_forms[0].text

        text = clause.node.leaves_string()
        verb = clause.structure('verb').lexical_form()

        od = od_structure.lexical_form()
        od_rewritten = od

        # lower case od if is not a proper name
        od_msi = od_structure.entity().msi
        if not self.is_proper_name(od_msi):
            od_rewritten = od[0].lower() + od[1:]

        if next_clause and next_clause.relative_entity == od_structure.entity():
            od_rewritten = od_rewritten + " " + next_clause.__repr__().strip()
            replacements = (verb, ''), (od, ''), (" " + next_clause.__repr__(), '')
        else:
            replacements = (verb, ''), (od, '')

        ntext = self.multiple_replace(text, *replacements).strip(' ')
        ntext = ntext[0].lower() + ntext[1:]

        ntext = "se " + rewritten_verb + " " + od_rewritten + " " + ntext
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

        ntext = ntext.replace('_', ' ').strip()
        return ntext

    def rewrite_clause_od_animated(self, node, sentence, clause, next_clause):

        # get the first leaf to extract the msi
        leaf = clause.verb.leaves()[0]

        msi = {"mode": leaf.msi["mode"],
               "time": leaf.msi["time"],
               "person": 3,
               "number": Number.singular}

        # transform the last leaf of verb (ie clause.verb) to the msi of the first leaf of verb
        lexical_forms = self.ontology.get_lexical_forms(clause.verb.lemma(), msi)
        rewritten_verb = lexical_forms[0].text

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
            repls = (verb, ''), (od, ''), (" " + next_clause.__repr__(), '')
        else:
            repls = (verb, ''), (od, '')

        ntext = self.multiple_replace(text, *repls).strip(' ')
        ntext = ntext[0].lower() + ntext[1:]

        if od_rewritten[0:3] == 'el ':
            od_rewritten = 'al ' + od_rewritten[3:]
        elif od_rewritten[0:3] == 'yo ' or od_rewritten[0:3] == 'yo':
            od_rewritten = 'a mí'
        else:
            od_rewritten = 'a ' + od_rewritten

        ntext = "se " + rewritten_verb + " " + od_rewritten + " " + ntext

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

        ntext = ntext.replace('_', ' ').strip()
        return ntext

    def is_proper_name(self, msi):
        is_not_proper_name = (msi['category'] != 'noun'
                              or (msi['category'] == 'noun' and msi['semantic_classification'] is None))
        return not is_not_proper_name

    def multiple_replacer(self, *key_values):
        replace_dict = dict(key_values)
        replacement_function = lambda match: replace_dict[match.group(0)]
        pattern = re.compile("|".join([re.escape(k) for k, v in key_values]), re.M)
        return lambda string: pattern.sub(replacement_function, string)

    def multiple_replace(self, string, *key_values):
        return self.multiple_replacer(*key_values)(string)

    type = "dislocation"
