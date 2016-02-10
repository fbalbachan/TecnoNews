#!/usr/bin/env python
#-*- coding: utf-8 -*-

import unittest

from src.model.paragraph.paragraph import Paragraph
from src.model.paragraph.paragraphAnalyzer import ParagraphAnalyzer
from src.model.sentence.sentence import Sentence
from src.model.sentence.sentenceAnalyzer import SentenceAnalyzer
from tests.freelingTreeRepository import FreelingTreeRepository
from tests.base_test import TestBase

class TokenizationTest(TestBase):
    @classmethod
    def setUpClass(self):
        print "[Tokenization test]"
        super(TokenizationTest, self).setUpClass()
        self.sentenceAnalyzer = SentenceAnalyzer(FreelingTreeRepository("tests/input/trees"))
        self.paragraphAnalyzer = ParagraphAnalyzer(self.sentenceAnalyzer)

    def test_single(self):
        self.kase("Leandro", (0, 7))
        self.kase("Leandro murió", (0, 7), (8, 13))

        # Numerales
        self.kase("Ésto costó 10.00", (0,4), (5, 10), (11, 16))

        # Puntuación
        self.kase("Era alto, bueno, amable.", (0, 3), (4, 8), (8, 9), (10, 15), (15, 16), (17, 23), (23, 24))

        # Enclíticos
        self.kase("Comiéndolos", (0, 8), (8, 11))

        # Contracciones
        self.kase("al", (0, 1), (1, 2))
        self.kase("Al", (0, 1), (1, 2))
        self.kase("del", (0, 2), (2, 3))
        self.kase("Del", (0, 2), (2, 3))

        # Formas léxicas compuestas
        self.kase("Leandro G. Liptak mató al Dr. Fernández", (0, 17), (18, 22), (23, 24), (24, 25), (26, 39))

        # BUG de Freeling: Dislocación de "buscó," en base a "lo cual"
        self.kase("El hombre buscó, lo cual llevó minutos", (0, 2), (3, 9), (10, 15), (15, 16), (17, 24), (25, 30), (31, 38))

        # BUG de Freeling: Dislocación de la ","
        self.kase("Destaco eso, en favor de lo cual vivo", (0, 7), (8, 11), (11, 12), (13, 24), (25, 32), (33, 37))

        # Idem anterior
        self.kase("Lloran, les molesta eso, que es mi amor.", (0, 6), (6, 7), (8, 11), (12, 19), (20, 23), (25, 28), \
                  (29, 31), (32, 34), (35, 39), (23, 24), (39, 40))

        self.kase('"Hola"', (0, 1), (1, 5), (5, 6))
        self.kase('«Hola»', (0, 1), (1, 5), (5, 6))
        self.kase('“Sótano”', (0, 1), (1, 7), (7, 8))

    def test_compound(self):
        self.kase_compound("Dr. Leandro Liptak", (0, 3), (4, 11), (12, 18))
        self.kase_compound("Leandro G. Liptak", (0, 7), (8, 10), (11, 17))
        self.kase_compound("lo cual", (0, 2), (3, 7))
        self.kase_compound("en favor de", (0, 2), (3, 8), (9, 11))

    def test_paragraph(self):
        self.kase_paragraph("Leandro amó. María también. Leandro amó.", [[(0, 7), (8, 11), (11, 12)],
                                                                         [(13, 18), (19, 26), (26, 27)],
                                                                         [(28, 35), (36, 39), (39, 40)]])

        self.kase_paragraph("Leandro amó, pero María odió.", [[(0, 7), (8, 11)],
                                                              [(18, 23), (24, 28), (28, 29)] ])

    def kase_paragraph(self, text, expected):
        paragraph = Paragraph.from_text(text)
        self.paragraphAnalyzer.analyze(paragraph)
        sentences = paragraph.sentences

        self.assertEqual(len(expected), len(sentences))
        for sentence, expected_components in zip(sentences, expected):
            self.kase_(sentence, *expected_components)

    def kase_compound(self, text, *expected_components):
        print "\tCase (compound):", text, "->",
        self.input = text
        sentence = Sentence(text)
        self.sentenceAnalyzer.analyze(sentence)

        token = sentence.parse_node.leaves()[0].token
        print token, token.components

        self.assertEqual((expected_components[0][0], expected_components[-1][1]), (token.start(), token.end()))

        self.assertEqual(list(expected_components), token.components)

    def kase(self, text, *expected_tokens):
        sentence = Sentence(text)
        self.input = text
        self.sentenceAnalyzer.analyze(sentence)
        self.kase_(sentence, *expected_tokens)

    def kase_(self, sentence, *expected_tokens):
        actual_tokens = [ (leaf.token.start(), leaf.token.end()) for leaf in sentence.parse_node.leaves() ]
        print "\tCase:", sentence.text, "->", actual_tokens
        self.assertEqual(actual_tokens, list(expected_tokens))

if __name__ == '__main__':
    unittest.main()
