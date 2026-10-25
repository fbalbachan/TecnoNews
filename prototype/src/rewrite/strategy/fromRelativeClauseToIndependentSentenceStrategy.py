# -*- coding: utf-8 -*-
__author__ = 'Alexis Balbachan'

import traceback
import sys
from collections import deque

from src.rewrite.rewrite import Rewrite
from src.rewrite.sentenceRewrite import SentenceRewrite
#from src.ling.numberEnum import NumberEnum
from src.utils.logger_utils import *
from src.utils.stringUtils import *
from src.model.tokenization.token import Token
import re

debug_mode = False


class FromRelativeClauseToIndependentSentenceStrategy:
    def __init__(self):
        if debug_mode: print("--> FromRelativeClauseToIndependentSentenceStrategy.init()")

    def applies_to(self, sentence, node):
        if debug_mode: print("--> FromRelativeClauseToIndependentSentenceStrategy.applies_to(sentence:", sentence.text, ")")
        result = False
        for clause in sentence.clauses:
            if self.applies_to_clause(clause, sentence):
                result = True

        return result

    def applies_to_clause(self, clause, sentence):
        if debug_mode: print("--> FromRelativeClauseToIndependentSentenceStrategy.applies_to_clause(", clause.node, ")")
        result = False
        if clause.is_relative():
            if any(linker_lexical in clause.relative_linker_words() for linker_lexical in ["quien", "quienes"]):

                sentence_before_clause = sentence.text[:clause.node.leaves()[0].token.start()].strip()

                #if sentence_before_clause[-1] ==  u",":
                #    result = True
                result = True

        return result

    def rewrite(self, sentence, node):
        for a_clause in sentence.clauses:
            if self.applies_to_clause(a_clause, sentence):
                original_sentence = sentence.text
                clause_start_index = a_clause.node.leaves()[0].token.start()
                clause_end_index = a_clause.node.leaves()[-1].token.end()
                #print clause_start_index
                #print clause_end_index
                #print original_sentence[clause_start_index:clause_end_index]
                #print a_clause.all_entities()[1].referent.designated_ref()


                for an_entity in a_clause.all_entities():
                    dereferenced_entity = an_entity.referent.designated_ref()
                    if not dereferenced_entity.is_tacit() and dereferenced_entity.is_named_entity() and dereferenced_entity.token.end() < clause_start_index:
                        #FOUND ENTITY! (Change possible underscores for spaces)
                        found_entity = re.sub('_', ' ', dereferenced_entity.lexical_form)

                        #Get entity pronoun for second sentence:
                        entity_pronoun = None
                        if dereferenced_entity.msi["gender"] == "masculine":
                            if dereferenced_entity.msi["number"] == "singular":
                                entity_pronoun =  "él"
                            else:
                                entity_pronoun = "ellos"
                        else:
                            if dereferenced_entity.msi["number"] == "singular":
                                entity_pronoun = "ella"
                            else:
                                entity_pronoun = "ellas"


                        #Extract sub clause, replace for pronoun, and clean:
                        new_second_sentence = original_sentence[:dereferenced_entity.token.start()] + entity_pronoun + " " + original_sentence[dereferenced_entity.token.end():clause_start_index].strip() + original_sentence[clause_end_index:].strip()
                        new_second_sentence = re.sub(',,', '', new_second_sentence)
                        new_second_sentence = re.sub(',\.', '.', new_second_sentence)
                        new_second_sentence = re.sub(r'(.),(.)', r'\1 \2', new_second_sentence)
                        new_second_sentence = re.sub(r',$', r'', new_second_sentence)
                        new_second_sentence = re.sub(r'\s{2,}', r' ', new_second_sentence)


                        new_first_sentence = original_sentence[clause_start_index:clause_end_index]
                        #Remove linker words:
                        new_first_sentence = new_first_sentence[a_clause.relative_linker[-1].token.end()-clause_start_index:].strip()

                        if new_first_sentence[-1] == ",":
                            new_first_sentence = new_first_sentence[:-1]


                        #Insert helper linkers:
                        after = False
                        for a_relative_linker in a_clause.relative_linker_words():
                            if a_relative_linker not in ["quien", "quienes"]:
                                new_first_sentence += " " + a_relative_linker
                                after = True

                        #Inser entity before or after:
                        if after:
                            new_first_sentence += " " + found_entity
                        else:
                            new_first_sentence = found_entity + " " + new_first_sentence

                        #Upper first char:
                        if len(new_first_sentence) > 1:
                            new_first_sentence = new_first_sentence[0].upper() + new_first_sentence[1:]
                        else:
                            new_first_sentence = new_first_sentence.upper()

                        if len(new_second_sentence) > 1:
                            new_second_sentence = new_second_sentence[0].upper() + new_second_sentence[1:]
                        else:
                            new_second_sentence = new_second_sentence.upper()

                        #Add missing period:
                        if new_first_sentence[-1] != '.':
                            new_first_sentence += "."

                        if new_second_sentence[-1] != '.':
                            new_second_sentence += "."


                        #print new_second_sentence
                        #print new_first_sentence
                        #print new_first_sentence + " " + new_second_sentence

                        new_text = new_first_sentence + " " + new_second_sentence

                        rewrite = Rewrite(sentence.parse_node, new_text)
                        return rewrite

    type = "dislocation"
