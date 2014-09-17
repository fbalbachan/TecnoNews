# -*- coding: utf-8 -*-
from src.rewrite.rewrite import Rewrite
from src.utils.stringUtils import set_first_letter_case
from src.model.go.conditionFinder import ConditionFinder


class AdverbialClauseDislocationStrategy:
    def applies_to(self, sentence):
        # No aplica a "Soy libre si amo a quien busca" porque ambas clauses, subord y subord-rel,
        # son hijas de "Soy libre". La clause subord-rel debería ser hija de la subord.
        main_clause = sentence.main_clause()
        
        return (
            main_clause.node.label == 'grup-verb' and len(main_clause.children) == 1 and
            main_clause.children[0].node.label == 'subord' and (
                main_clause.children[0].node.token.start() == main_clause.node.token.start() or
                len(ConditionFinder(main_clause.children[0]).find()) == 0
            )
        )

    def rewrite(self, sentence):
        main_clause = sentence.main_clause()
        if main_clause.children[0].node.token.start() == main_clause.node.token.start():
            return self.rewrite_if_p_q(sentence)
        else:
            return self.rewrite_q_if_p(sentence)

    def rewrite_if_p_q(self, sentence):
        main_clause = sentence.main_clause()
        token = main_clause.children[0].node.token

        text = sentence.paragraph.text.decode("utf-8")
        first_part = text[main_clause.node.token.start():token.end()].strip()
        second_part = text[token.end():main_clause.node.token.end()].strip()

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
        return Rewrite(sentence.main_clause().node, rewritten_sentence.encode('utf-8'))

    def rewrite_q_if_p(self, sentence):
        main_clause = sentence.main_clause()
        token = main_clause.children[0].node.token

        text = sentence.paragraph.text.decode("utf-8")
        first_part = text[main_clause.node.token.start():token.start()].strip()
        second_part = text[token.start():token.end()].strip()
        third_part = text[token.end():main_clause.node.token.end()].strip()

        final_punctuation = "" # TODO: Tomar toda la puntuación del final de third_part
        if len(third_part) > 0 and third_part[-1] == ".": # TODO: Hacerlo bien: Si soy esto, soy esto!. (múltiples puntuaciones)
            final_punctuation = "."
            third_part = third_part[:-1]

        if first_part[-1] == ",":
            first_part = first_part[:-1]

        if second_part[-1] != ",":
            second_part += ","
        second_part = set_first_letter_case(first_part, second_part)

        # TODO: Evaluar los casos donde esto no debe hacerse! (Ej: nombres propios)
        first_part = first_part[0].lower() + first_part[1:]
        if len(third_part) > 0:
            # TODO: Evaluar los casos donde esto no debe hacerse! (Ej: nombres propios)
            third_part = " " + third_part[0].lower() + third_part[1:]

        rewritten_sentence = second_part + " " + first_part + third_part + final_punctuation
        return Rewrite(sentence.main_clause().node, rewritten_sentence.encode('utf-8'))

    type = "dislocation"
