# -*- coding: utf-8 -*-
from src.rewrite.rewrite import Rewrite
from src.utils.stringUtils import set_first_letter_case
from src.model.sentence.sentence import Sentence


class AdverbialClauseDislocationStrategy:
    def __init__(self, ontology):
        self.ontology = ontology

    def applies_to(self, sentence):
        # TODO: Decidir si verificar tipos en applies_to(), si usar clauses con main_clause()
        # agregando la sentence accesible desde las clauses, o si usar diferentes tipos de estrategias
        # para sentences y clauses.
        if not isinstance(sentence, Sentence): return False
        
        # No aplica a "Soy libre si amo a quien busca" porque ambas clauses, subord y subord-rel,
        # son hijas de "Soy libre". La clause subord-rel debería ser hija de la subord.
        main_clause = sentence.main_clause()
        
        # TODO: Consultar sobre la property que da str(...) = 'grup-verb'
        return str(main_clause.node) == 'grup-verb' and len(main_clause.children) == 1\
            and str(main_clause.children[0].node) == 'subord'

    def rewrite(self, sentence):
        main_clause = sentence.main_clause()
        
        first_part = str(sentence)[:main_clause.children[0].node.token.end()+1].strip()
        second_part = str(sentence)[main_clause.children[0].node.token.end()+1:].strip()
        final_punctuation = '' # TODO: Tomar toda la puntuación del final de second_part
        # TODO: Quitar la final_punctuation de second_part
        if first_part[-1] == ",":
            first_part = first_part[:-1]
            second_part += ","
        second_part = set_first_letter_case(first_part, second_part)
        # TODO: Check cases when lowercase on [0] it's not appropriate
        rewritten_sentence = second_part + " " + first_part[0].lower() + first_part[1:] + final_punctuation
        return Rewrite(sentence.main_clause().node, rewritten_sentence)
