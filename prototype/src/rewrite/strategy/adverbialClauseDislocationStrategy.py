# -*- coding: utf-8 -*-
from src.rewrite.rewrite import Rewrite
from src.utils.stringUtils import set_first_letter_case
from src.model.go.conditionFinder import ConditionFinder


class AdverbialClauseDislocationStrategy:
    def applies_to(self, sentence):
        main_clause = sentence.main_clause()

        en_caso_de_que = (
            main_clause.node.label == 'prep' and
            self.is_subord_to_apply(main_clause.children[0], ["que"]) and
            len(ConditionFinder(main_clause.children[0].children[0]).find()) > 0 and
            ConditionFinder(main_clause.children[0].children[0]).find()[0].object == 'en_caso_de'
        )

        return self.is_subord_to_apply(main_clause) or en_caso_de_que

    def is_subord_to_apply(self, clause,
            # "en_caso_de" se ve por separado en applies_to()
            subordinate_headers = ["si", "mientras", "cuando", "una_vez_que"]
        ):
        return (
            clause.node.label == 'grup-verb' and len(clause.children) > 0 and
            clause.children[0].node.label == 'subord' and (
                clause.children[0].node.token.start() == clause.node.token.start() or
                len(ConditionFinder(clause.children[0]).find()) == 0
            ) and
            clause.children[0].node.leaves()[0].lemma in subordinate_headers
        )

    def rewrite(self, sentence):
        main_clause = sentence.main_clause()
        if self.is_subord_to_apply(main_clause):
            if main_clause.children[0].node.token.start() == main_clause.node.token.start():
                return self.rewrite_if_p_q(sentence)
            else:
                return self.rewrite_q_if_p(sentence)
        else:
            return self.rewrite_en_caso_de_que_p_q(sentence)

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
        return Rewrite(main_clause.node, rewritten_sentence.encode('utf-8'))

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
        return Rewrite(main_clause.node, rewritten_sentence.encode('utf-8'))

    def rewrite_en_caso_de_que_p_q(self, sentence):
        main_clause = sentence.main_clause()
        clause = main_clause.children[0]
        token = clause.children[0].node.token
        
        text = sentence.paragraph.text.decode("utf-8")
        first_part = text[clause.node.token.start():token.end()].strip()
        second_part = text[token.end():clause.node.token.end()].strip()

        final_punctuation = "" # TODO: Tomar toda la puntuación del final de second_part
        if len(second_part) > 0 and second_part[-1] == ".": # TODO: Hacerlo bien: Si soy esto, soy esto!. (múltiples puntuaciones)
            final_punctuation = "."
            second_part = second_part[:-1]

        if first_part[-1] == ",":
            first_part = first_part[:-1]

        second_part += ","
        second_part = set_first_letter_case(text[main_clause.node.token.start()], second_part)

        # first_part[0] nunca debe ser mayúscula ya que comienza con "en caso de"
        first_part = first_part[0].lower() + first_part[1:]

        rewritten_sentence = second_part + " en caso de " + first_part + final_punctuation
        return Rewrite(main_clause.node, rewritten_sentence.encode('utf-8'))

    type = "dislocation"
