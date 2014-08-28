#!/usr/bin/env python
#-*- coding: utf-8 -*-

import unittest

from src.model.sentence.sentence import Sentence
from src.model.sentence.sentenceAnalyzer import SentenceAnalyzer
from tests.freelingTreeRepository import FreelingTreeRepository


class TokenizationTest(unittest.TestCase):
    def setUp(self):
        print "[Tokenization test]"

        self.sentenceAnalyzer = SentenceAnalyzer(FreelingTreeRepository("tests/input/trees"))

    def test(self):
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

    def kase(self, text, *expected_tokens):
        print "\tCase:", text, "->",

        sentence = Sentence(text)
        self.sentenceAnalyzer.analyze(sentence)

        actual_tokens = [ (leaf.token.start(), leaf.token.end()) for leaf in sentence.parse_node.leaves() ]
        print actual_tokens

        self.assertEqual(actual_tokens, list(expected_tokens))

if __name__ == '__main__':
    unittest.main()