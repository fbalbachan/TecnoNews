# -*- coding: utf-8 -*-
__author__ = 'Martín Caramés Abente'

import traceback
import sys
from collections import deque

from src.rewrite.rewrite import Rewrite
from src.rewrite.sentenceRewrite import SentenceRewrite
from src.ling.number import Number
from src.utils.logger_utils import *
from src.utils.stringUtils import *
from src.model.tokenization.token import Token

debug_mode = False


class AppositionDislocationStrategy:
    def __init__(self):
        if debug_mode: print("--> AppositionDislocationStrategy.init()")

    def applies_to(self, sentence, node):
        if debug_mode: print("--> AppositionDislocationStrategy.applies_to(sentence:", sentence.text, ")")
        result = False
        for clause in sentence.clauses:
            if self.applies_to_clause(clause):
                result = True

        return result

    def applies_to_clause(self, clause):
        if debug_mode: print("--> AppositionDislocationStrategy.applies_to_clause(", clause.node, ")")
        result = False
        for structure in clause.syntactic_structures:
            for entity in structure.all_entities():
                if hasattr(entity, 'appositions') and entity.appositions:
                    result = True

        return result

    def rewrite(self, sentence, node):
        if debug_mode: print("--> AppositionDislocationStrategy.rewrite(sentence:", sentence, ", node:", node, ")")

        rewrite = None

        try:
            new_sentence_texts = []
            replacements = []
            for clause in sentence.clauses:
                if self.applies_to_clause(clause):
                    [replacements, new_sentence_texts] = self.rewrite_clause(sentence,
                                                                             clause,
                                                                             replacements,
                                                                             new_sentence_texts)
            new_text = self.compose_text(replacements, sentence.text)

            for new_sentence_text in new_sentence_texts:
                new_text += " " + new_sentence_text

            rewrite = Rewrite(sentence.parse_node, new_text)

        except Exception as e:
            msg = (": " + str(e)) if e and hasattr(e, "message") else ""
            logger = get_logger('tecnonews')
            logger.info("AppositionDislocationStrategy Rewriting:")
            logger.info(msg)
            ex_type, ex, tb = sys.exc_info()
            logger.info(traceback.format_tb(tb))

        if debug_mode: print("<-- AppositionDislocationStrategy.rewrite()")
        return rewrite

    def compose_text(self, rewrites, text):
        if debug_mode: print("--> AppositionDislocationStrategy.compose_text(rewrites, text:", text, ")")
        rewrites.sort(key=lambda rewrite_rule: rewrite_rule.token.start())
        rewrites_queue = deque(rewrites)


        offset = 0
        while rewrites_queue:
            rewrite = rewrites_queue.popleft()
            new_token = Token()
            new_token.append(rewrite.token.start()+offset, rewrite.token.end()+offset)
            new_rewrite = SentenceRewrite(text, new_token, rewrite.replacement_text[:])
            local_offset = len(rewrite.replacement) - len(rewrite.sentence_text)
            text = new_rewrite.replacement
            offset += local_offset

        if debug_mode: print("<-- AppositionDislocationStrategy.compose_text() --> ", text)
        return text

    def rewrite_clause(self, sentence, clause, replacements, sentence_texts):
        """

         "Pescamos bagres, los tiburones del río, el fin de semana, despreocupadamente."

           --> "Pescamos bagres el fin de semana, despreocupadamente. Bagres son los tiburones del río."
               1) ", los tiburones del río," --> ""
               2) New sentence: "(B)agres (son) los tiburones del río(.)"
        """
        if debug_mode: print("--> AppositionDislocationStrategy.rewrite_clause(sentence:", sentence, ", clause:", clause, ")")

        appositions = self.get_appositions(clause)
        for apposition in appositions:
            replacement = self.replacement_for_head_and_tail(sentence, apposition)
            replacements.append(replacement)

            new_sentence_text = self.get_new_sentence_text(sentence, apposition)
            sentence_texts.append(new_sentence_text)

        if debug_mode:
            print("<-- AppositionDislocationStrategy.rewrite_clause: ")
            print("replacements: ", replacements)
            print("new_sentence_texts: ", sentence_texts)

        return [replacements, sentence_texts]

    def get_appositions(self, clause):
        if debug_mode: print("--> AppositionDislocationStrategy.get_appositions()")
        appositions = []
        for structure in clause.syntactic_structures:
            for entity in structure.all_entities():
                if hasattr(entity, 'appositions') and entity.appositions:
                    appositions.append(entity)

        return appositions

    def replacement_for_head_and_tail(self, sentence, appositions_head):

        token = self.find_apposition_token(sentence, appositions_head)

        token_replacement = self.get_replace_string_for(sentence, appositions_head)

        # First entity never transforms its first letter from upper to lower case.
        rewrite_rule = SentenceRewrite.preserving_case(sentence.text, token, token_replacement)

        return rewrite_rule

    def get_replace_string_for(self, sentence, entity):
        if debug_mode: print("--> AppositionDislocationStrategy.get_replace_string_for(entity:", entity, ")")

        origin = sentence.token.start()
        start_idx = entity.node.token.start() - origin

        # This takes into account a possible leapfrogged node (based on apposition def.)
        last_leaf = entity.node.leaves()[-1]
        if last_leaf.lexical_form in [","]:
            end_idx = last_leaf.token.start() - origin                          # Index points to the comma
        else:
            end_idx = entity.node.token.end() - origin
            end_idx = sentence.text.find(",", end_idx, -1)     # Index points to the comma

        result = sentence.text[start_idx:end_idx].replace('_', ' ')

        if debug_mode: print("<-- AppositionDislocationStrategy.get_replace_string_for() --> ", result)
        return result

    def find_apposition_token(self, sentence, appositions_head):
        """ Find the apposition's token relative to the sentence beginning """

        token = Token()
        start = self.find_apposition_start(sentence, appositions_head)
        end = self.find_apposition_end(sentence, appositions_head)
        token.append(start, end)
        return token

    def find_apposition_start(self, sentence, appositions_head):
        start = appositions_head.token.start()
        for apposition in appositions_head.appositions:
            if apposition.token.start() < start:
                start = apposition.token.start()

        relative_start = start - sentence.token.start()

        return relative_start

    def find_apposition_end(self, sentence, appositions_head):
        """ Finds the index for the apposition's end, relative to sentence beginning

        :param sentence: Sentence containing the apposition
        :param appositions_head: Apposition's head entity
        :rtype: integer between 0 and len(sentence.text)
        """

        origin = sentence.token.start()
        elements = [appositions_head] + appositions_head.appositions

        relative_end = 0
        for element in elements:
            link_relative_end = element.token.end() - origin
            if link_relative_end > relative_end:
                relative_end = link_relative_end

                # This takes into account a possible leapfrogged node (based on apposition def.)
                last_leaf = element.node.leaves()[-1]
                if last_leaf.lexical_form in [","]:
                    relative_end = last_leaf.token.end() - origin       # Point to the char following the comma
                else:
                    relative_end = sentence.text.find(",", relative_end, -1) + 1

        return relative_end

    def get_new_sentence_text(self, sentence, apposition):
        if debug_mode: print("--> AppositionDislocationStrategy.get_new_sentence_text(apposition:", apposition, ")")

        head = self.get_replace_string_for(sentence, apposition)

        # Uppercase for the beginning of a sentence
        head = head[0].upper() + head[1:]

        verb = "son" if apposition.number() == Number.plural else "es"

        tail_first = self.get_replace_string_for(sentence, apposition.appositions[0])

        # Lowercase for the second part of the sentence
        tail_first = tail_first[0].lower() + tail_first[1:]

        sentence_text = head + " " + verb + " " + tail_first + "."

        if debug_mode: print("<-- AppositionDislocationStrategy.get_new_sentence_text() --> ", sentence_text)
        return sentence_text

    type = "dislocation"
