#!/usr/bin/env python
#-*- coding: utf-8 -*-
import unittest

from src.model.sentence.sentenceAnalyzer import SentenceAnalyzer
from src.model.sentence.sentence import Sentence
from tests.freelingTreeRepository import FreelingTreeRepository
from tests.base_test import TestBase

class TestRegimen(TestBase):

    def setUp(self):
        super(TestRegimen, self).setUp()
        self.input_texts_with_regimen = [
            ('todos los cuatrimestres yo lidio con mis alumnos', 'mis alumnos'),
        ]

    def test_get_regimen(self):
        analyzer = SentenceAnalyzer(FreelingTreeRepository("tests/input/trees"))

        for (input_text, expected_regimen) in self.input_texts_with_regimen:
            print "trying: %s .. " % input_text,

            self.input = input_text

            sentence = Sentence(input_text)
            analyzer.analyze(sentence)

            self.assertEqual(1, len(sentence.clauses), "La oración tiene más de una cláusula.")
            clause = sentence.clauses[0]

            self.assertEquals("active", clause.voice)

            self.assertEquals(expected_regimen, clause.structure("regimen").lexical_form())

            print "OK"

if __name__ == '__main__':
    unittest.main()
