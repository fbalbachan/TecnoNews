#!/usr/bin/env python
#-*- coding: utf-8 -*-
from ast import literal_eval
import unittest

from csv_file_reader import load_csv_test_file
from src.model.freelingSentenceAnalyzer import FreelingSentenceAnalyzer
from src.model.sentence import *
from tests.freelingTreeRepository import FreelingTreeRepository


class TestSentence(unittest.TestCase):

    def setUp(self):
        self.input_texts = load_csv_test_file('tests/input/sentence_test.csv')

    def test_passive_or_active(self):
        analyzer = FreelingSentenceAnalyzer(FreelingTreeRepository("tests/input/trees"))

        for (input_text, active, passive, unimember) in self.input_texts:
            print "trying: %s .. " % input_text,

            sentence = Sentence(input_text)
            analyzer.analyze(sentence)

            self.assertEqual(1, len(sentence.clauses), "La oración tiene más de una cláusula.")

            voice = sentence.clauses[0].voice
            expected_voice = "active" if literal_eval(active) else "passive" if literal_eval(passive) else None
            self.assertEquals(voice, expected_voice, "La voz de la oración es incorrecta.")

            print "OK"

if __name__ == '__main__':
    unittest.main()
