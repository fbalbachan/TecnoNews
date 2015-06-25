# -*- coding: utf-8 -*-

__author__ = 'Martín Caramés Abente'

import traceback
import sys

from src.rewrite.rewrite import Rewrite
from src.rewrite.sentenceRewrite import SentenceRewrite
from collections import deque
from src.utils.logger_utils import *
from src.model.tokenization.token import Token

debug_mode = False


class SeImpersonalStrategy:
    def __init__(self):
        if debug_mode: print "--> SeImpersonalStrategy.init()"

    def applies_to(self, sentence, node):
        if debug_mode: print "--> SeImpersonalStrategy.applies_to(sentence:", sentence.text, ")"
        result = False
        for clause in sentence.clauses:
            if self.applies_to_clause(clause):
                result = True

        return result

    def applies_to_clause(self, clause):
        if debug_mode: print "--> SeImpersonalStrategy.applies_to_clause(", clause.node, ")"
        result = False
        for structure in clause.syntactic_structures:
            for entity in structure.all_entities():
                if hasattr(entity, 'appositions') and entity.appositions:
                    result = True

        return result

    def rewrite(self, sentence, node):
        if debug_mode: print "--> SeImpersonalStrategy.rewrite(sentence:", sentence, ", node:", node, ")"

        new_text = sentence.text
        new_sentence_texts = []
        replacements = []

        try:
            for clause in sentence.clauses:
                if self.applies_to_clause(clause):
                    [replacements, new_sentence_texts] = self.rewrite_clause(sentence,
                                                                             clause,
                                                                             replacements,
                                                                             new_sentence_texts)
            new_text = self.compose_text(replacements, new_text)

            for new_sentence_text in new_sentence_texts:
                new_text += u" " + new_sentence_text

        except Exception as e:
            msg = (": " + e.message) if e and hasattr(e, "message") else ""
            logger = get_logger('tecnonews')
            logger.info("SeImpersonalStrategy Rewriting:")
            logger.info(msg)
            ex_type, ex, tb = sys.exc_info()
            logger.info(traceback.format_tb(tb))

        rewrite = Rewrite(sentence.parse_node, new_text.encode("utf-8"))

        if debug_mode: print "<-- SeImpersonalStrategy.rewrite()"
        return rewrite

    def compose_text(self, rewrites, text):
        rewrites.sort(key=lambda rewrite_rule: rewrite_rule.token.start())
        rewrites_queue = deque(rewrites)

        if type(text) != unicode:
            text = text.decode("utf-8")

        offset = 0
        while rewrites_queue:
            rewrite = rewrites_queue.popleft()
            new_token = Token()
            new_token.append(rewrite.token.start()+offset, rewrite.token.end()+offset)
            new_rewrite = SentenceRewrite(text, new_token, rewrite.token_replacement[:])
            local_offset = len(rewrite.replacement) - len(rewrite.sentence_text)
            text = new_rewrite.replacement
            offset += local_offset

        if debug_mode: print "\n<-- compose_text()\n"
        return text

    def rewrite_clause(self, sentence, clause, replacements, sentence_texts):
        """
        """
        for elem in []:
            replacement = elem
            replacements.append(replacement)

            new_sentence_text = self.get_new_sentence_text(sentence)
            sentence_texts.append(new_sentence_text)

        if debug_mode: print "\n<-- rewrite_clause()\n"
        return [replacements, sentence_texts]

    def get_replace_string_for(self, sentence, entity):

        origin = sentence.token.start()
        start_idx = entity.node.token.start() - origin

        # This takes into account a possible leapfrogged node (based on apposition def.)
        last_leaf = entity.node.leaves()[-1]
        if last_leaf.lexical_form in [u","]:
            end_idx = last_leaf.token.start() - origin                          # Index points to the comma
        else:
            end_idx = entity.node.token.end() - origin
            end_idx = sentence.text.decode("utf-8").find(u",", end_idx, -1)     # Index points to the comma

        result = sentence.text.decode("utf8")[start_idx:end_idx].replace('_', ' ')
        return result

    def get_new_sentence_text(self, sentence):
        if debug_mode: print "--> SeImpersonalStrategy.get_new_sentence_text()"

        head = u"HEAD"
        verb = u"VERB"
        tail = u"TAIL"
        sentence_text = head + u" " + verb + u" " + tail + u"."

        return sentence_text

    type = "dislocation"


