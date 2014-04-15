#!/usr/bin/env python
#-*- coding: utf-8 -*-
import unittest

from src.model.freelingSentenceAnalyzer import FreelingSentenceAnalyzer
from src.model.sentence import Sentence
from tests.csv_file_reader import load_csv_test_file
from tests.freelingTreeRepository import FreelingTreeRepository


class TestOD(unittest.TestCase):

    def setUp(self):
        self.input_texts_with_ods = load_csv_test_file('tests/input/od_test.csv')

    def test_get_OD(self):
        analyzer = FreelingSentenceAnalyzer(FreelingTreeRepository("tests/input/trees"))

        for (input_text, expected_od) in self.input_texts_with_ods:
            print "trying: %s .. " % input_text,

            sentence = Sentence(input_text)
            analyzer.analyze(sentence)

            self.assertEqual(1, len(sentence.clauses), "La oración tiene más de una cláusula.")
            clause = sentence.clauses[0]

            self.assertEquals("active", clause.voice)

            if expected_od == "None":
                self.assertTrue(not clause.has_structure("od") or clause.structure("od").is_empty())
            else:
                self.assertEquals(expected_od, clause.structure("od").lexical_form())

            print "OK"

if __name__ == '__main__':
    unittest.main()
