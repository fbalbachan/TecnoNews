# -*- coding: utf-8 -*-
from src.rewrite.rewrite import Rewrite
from src.utils.stringUtils import set_first_letter_case
from src.parser.leafNode import LeafNode
from src.parser.labelNode import LabelNode

import random


class SegunToDijoDislocationStrategy:
    def __init__(self, dislocation = [ True, False ], changes = ["de_acuerdo_con", ""]):
        self.dislocation = dislocation
        self.changes = changes

    def applies_to(self, sentence, node):
        return self.applies_segun_inicial(sentence, node)


      
        

    def applies_segun_inicial(self, sentence, node):
        return isinstance(node, LabelNode) and node.label == 'subord' and (
            len(node.children) >= 3 and
            isinstance(node.children[0], LeafNode) and node.children[0].lemma == 'según' and
            isinstance(node.children[1], LabelNode) and node.children[1].label == 'sn' and
            self.correct_last_quotes(node, sentence) > 0
        )




    def is_quote(self, node, sentence):
        token = node.token
        
        return isinstance(node, LabelNode) and node.label == 'F-no-c' and\
            sentence.paragraph.text.decode("utf-8")[token.start():token.end()].encode('utf-8') == '"'

    def correct_last_quotes(self, node, sentence):
        if self.is_quote(node.children[2], sentence):
            for i in xrange(3, len(node.children)):
                if self.is_quote(node.children[i], sentence): return i
        return -1

    def rewrite(self, sentence, node):
        if self.applies_segun_inicial(sentence, node):
            return self.rewrite_segun_inicial(sentence, node)
        # TODO: This code is for a future else
        return self.rewrite_segun_inicial(sentence, node)

    def rewrite_segun_inicial(self, sentence, node):
        rewrite_selected = False
        rewrite_selection_tries = 15 # To avoid infinite loop
                                     # with probability = (1/4^15)
        while rewrite_selection_tries > 0 and not rewrite_selected:
            dislocation = random.choice(self.dislocation)
            change = random.choice(self.changes)
            if dislocation or change == "de_acuerdo_con":
                rewrite_selected = True
            else:
                rewrite_selection_tries -= 1

        text = sentence.paragraph.text.decode("utf-8")

        last_quote_index = self.correct_last_quotes(node, sentence)
        last_quote_token = node.children[last_quote_index].token

        if change == "de_acuerdo_con":
            segun = text[node.token.start():node.children[0].token.end()].strip()
            first_part = text[node.children[1].token.start():node.children[1].token.end()].strip()
            first_part = set_first_letter_case(segun, "de acuerdo con ") + first_part
        else:
            first_part = text[node.token.start():node.children[1].token.end()].strip()

        

        second_part = text[node.children[2].token.start():last_quote_token.end()].strip()
        third_part = text[last_quote_token.end():node.token.end()].strip()

        if dislocation:
            if first_part[-1] == ",":
                first_part = first_part[:-1]

            second_part += ","
            if first_part[0] == first_part[0].lower():
                second_part = second_part[0] + second_part[1].lower() + second_part[2:]
            elif first_part[0] == first_part[0].upper():
                second_part = second_part[0] + second_part[1].upper() + second_part[2:]
            second_part = set_first_letter_case(first_part[1], second_part)

            # first_part[0] nunca debe ser mayúscula ya que comienza con "según" o similares
            first_part = first_part[0].lower() + first_part[1:]

            rewritten_sentence = second_part + " " + first_part + third_part
        else:
            rewritten_sentence = first_part + " " + second_part + third_part
        return Rewrite(node, rewritten_sentence.encode('utf-8'))

    type = "dislocation"
