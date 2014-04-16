#!/usr/bin/env python
#-*- coding: utf-8 -*-
import unittest

from src.model.freelingSentenceAnalyzer import FreelingSentenceAnalyzer
from src.model.sentence import Sentence
from tests.freelingTreeRepository import FreelingTreeRepository


class TestEquative(unittest.TestCase):

    def setUp(self):
        self.input_texts_with_equative = [
            ('Fulano me parece una buena persona', 'una buena persona'),
            ('Fulano es un hombre huraño y taciturno', 'un hombre huraño y taciturno'),
        ]

    def test_get_equative(self):
        analyzer = FreelingSentenceAnalyzer(FreelingTreeRepository("tests/input/trees"))

        for (input_text, expected_equative) in self.input_texts_with_equative:
            print "trying: %s .. " % input_text,

            sentence = Sentence(input_text)
            analyzer.analyze(sentence)

            self.assertEqual(1, len(sentence.clauses), "La oración tiene más de una cláusula.")
            clause = sentence.clauses[0]

            self.assertEquals("active", clause.voice)
            self.assertEquals(expected_equative, clause.structure("equative").lexical_form())

            print "OK"


if __name__ == '__main__':
    unittest.main()
