# -*- coding: utf-8 -*-
from src.rewrite.rewrite import Rewrite
from src.utils.stringUtils import set_first_letter_case
from src.parser.leafNode import LeafNode
from src.parser.labelNode import LabelNode


class AlthoughClauseDislocationStrategy:
    def applies_to(self, sentence):
        node = sentence.parse_node
        if node.label != 'coor-vb': return False
        aunque = False
        for i in xrange(len(node.children)):
            child = node.children[i]
            if isinstance(child, LeafNode) and child.lemma == 'aunque':
                aunque = True
                break
        if i > 0: return False # TODO: Quitar esta línea para incorporar q, aunque p
        if not aunque or i == len(node.children) - 1: return False
        if isinstance(node.children[i+1], LabelNode) and node.children[i+1].label != 'grup-verb': return False
        if len([ c for c in node.children if isinstance(c, LabelNode) and c.label == 'grup-verb' ]) < 2: return False
        return True

    def rewrite(self, sentence):
        return self.rewrite_although_p_q(sentence)

    def rewrite_although_p_q(self, sentence):
        node = sentence.parse_node
        token = node.children[1].token

        text = sentence.paragraph.text.decode("utf-8")
        first_part = text[node.token.start():token.end()].strip()
        second_part = text[token.end():node.token.end()].strip()

        # TODO: Use punctuation code better
        while ",.!:;".find(second_part[0]) >= 0:
            second_part = second_part[1:]
        second_part = second_part.strip()

        final_punctuation = "" # TODO: Tomar toda la puntuación del final de second_part
        if len(second_part) > 0 and second_part[-1] == ".": # TODO: Hacerlo bien: Si soy esto, soy esto!. (múltiples puntuaciones)
            final_punctuation = "."
            second_part = second_part[:-1]

        if first_part[-1] == ",":
            first_part = first_part[:-1]

        second_part += ","
        second_part = set_first_letter_case(first_part, second_part)

        # first_part[0] nunca debe ser mayúscula ya que comienza con condicionales
        first_part = first_part[0].lower() + first_part[1:]

        rewritten_sentence = second_part + " " + first_part + final_punctuation
        return Rewrite(node, rewritten_sentence.encode('utf-8'))

    type = "dislocation"
