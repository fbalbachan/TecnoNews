#-*- coding: utf-8 -*-
from src.rewrite.rewrite import Rewrite
from src.utils.collectionUtils import dict_by
from src.utils.stringUtils import set_first_letter_case
from src.model.entity.tacitEntity import TacitEntity

import ConfigParser
import re
import sys, traceback # TODO: remove

# TODO: process all the clausules where the rewrite can be made
# TODO: check when 'a' is added before an 'el'
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
            clauses = [clause for clause in sentence.clauses if self.applies_to_clause(clause)]
        except Exception as e:
                # print e.message
                ex_type, ex, tb = sys.exc_info()
                traceback.print_tb(tb)
                raise
        return self.rewrite_clause(node, sentence, clauses)

    def applies_to_clause(self, clause):
        return self.is_complete(clause) and clause.voice == 'passive' and \
               clause.verb and clause.verb.transitivity == 'TRANSITIVE' and\
               clause.node.label == "verb-pass"

    def is_complete(self, clause):
        # print "is_complete"
        # print "clause", clause
        # print "clause.node", clause.node
        # print "clause.proper_tree()", clause.proper_tree()
        # print "clause.has_structure('subject')", clause.has_structure('subject')
        # if clause.has_structure('subject'):
        #     print "clause.structure('subject').is_tacit()", clause.structure('subject').is_tacit()
        # print "clause.has_structure('od')", clause.has_structure('od')
        # try:
        #     if clause.has_structure('od'):
        #         print clause.structure('od')
        #         print "clause.structure('od').is_tacit()", clause.structure('od').is_tacit()
        #         if clause.structure('od').is_tacit():
        #             print "clause.structure('od').coref_chain", clause.structure('od').entity().coref_chain
        #         if clause.structure('od').entity().coref_chain != [] and clause.structure('od').is_tacit():
        #             print "clause.structure('od').entity().referenced()", \
        #             clause.structure('od').entity().referenced()
        # except Exception as e:
        #     print e.message
        #     ex_type, ex, tb = sys.exc_info()
        #     traceback.print_tb(tb)
        #     raise
        # print "is_complete", clause.has_structure('subject') and not clause.structure('subject').is_tacit() and \
        #        clause.has_structure('od') and not clause.structure('od').is_tacit()
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
        # try:
        # kernel is not defined if is
        if od.is_tacit():
            return True
        else:
            if od.kernel.lemma in self.persons \
                    or od.kernel.lemma in self.demonym\
                    or od.msi['semantic_classification'] == 'person':
                return True

        return False

    def rewrite_clause(self, node, sentence, clauses):
        # grouped = self.grouped_references_for(clause)
        # groups_with_position = [ (group, self.position_of(group, clause)) for group in grouped ]
        #
        # source_leaves = self.source_leaves_for(clause)
        #
        # text = self.compose_text_for(source_leaves, groups_with_position, clause)
        # print "----Clauses:", clauses
        clause = clauses[0]

        try:

            # print "self.is_animated(clause.structure('od').entity())", self.is_animated(clause.structure('od').entity())
            # get the first leaf to extract the msi
            leaf = clause.verb.leaves()[0]
            # print "leaf.msi", leaf.msi
            # number person mode, time

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

            od_msi = clause.structure('od').entity().msi
            if not self.is_proper_name(od_msi):
                od_rewritten = od[0].lower() + od[1:]

            # assumption: is always a "por" before the OD in the original clause
            if self.is_animated(clause.structure('od').entity()):
                 od_rewritten = 'a ' + od_rewritten

            repls = (verb, rewrited_verb), (subject_pattern, od_rewritten), (od, subject_rewritten)

            verb_leaves = clause.structure('verb').entity().leaves()
            subject_leaves = clause.structure('subject').entity().leaves()
            clause_nds_idx = clause.proper_leaves()[-1].token.end()
            # print "clause node leaves", clause.node.leaves()
            #
            # print "sentence.token", sentence.token
            # print "clause.proper_leaves()", clause.proper_leaves()
            # print "clause.proper_leaves()[-1]", clause.proper_leaves()[-1]
            # print "clause.proper_leaves()[-1]", clause.proper_leaves()[-1].token.start()
            # print "clause.proper_leaves()[-1].token.start", clause.proper_leaves()[-1].token.end()
            # print "clause.proper_leaves()[-1].token.ends", clause.proper_leaves()[-1].token.end()
            # print "clause.proper_leaves()[-1].token.start/ends", sentence.text[clause.proper_leaves()[-1].token.start():clause.proper_leaves()[-1].token.end()]
            #
            # print "clause_nds_idx", clause_nds_idx
            # print "sentence.text", sentence.text
            # print "sentence.text[clause_nds_idx]", sentence.text[clause_nds_idx]
            # print "text before clause ends :", sentence.text[:clause_nds_idx]
            # print "text after clause ends:", sentence.text[clause_nds_idx:]
            #
            # print "subject_leaves", subject_leaves[0]

            # reemplace verb TODO: valida use of indices in several cases
            # text = text[:verb_leaves[0].token.start()] + rewrited_verb + text[verb_leaves[-1].token.end():]

            ntext = self.multiple_replace(text, *repls)

            # If OD is tacit
            if clause.structure('od').is_tacit():
                ntext = subject_rewritten + " " + ntext

            # TODO: check if the first letter of the clausele is the first of the sentence
            #     ntext = ntext[0].upper() + ntext[1:]

        except Exception as e:
                print e.message
                ex_type, ex, tb = sys.exc_info()
                traceback.print_tb(tb)
        return Rewrite(clause.node, ntext.replace('_', ' '))


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
