#!/usr/bin/env python
#-*- coding: utf-8 -*-
import unittest

from src.model.sentence.sentenceAnalyzer import SentenceAnalyzer
from src.model.sentence.sentence import Sentence
from tests.csv_file_reader import load_csv_test_file
from tests.freelingTreeRepository import FreelingTreeRepository
from tests.base_test import TestBase

class TestOD(TestBase):

    def setUp(self):
        super(TestOD, self).setUp()
        self.input_texts_with_ods = load_csv_test_file('tests/input/od_test.csv')

    def test_get_OD(self):
        analyzer = SentenceAnalyzer(FreelingTreeRepository("tests/input/trees"))

        for (input_text, expected_od) in self.input_texts_with_ods:
            print "trying: %s .. " % input_text,

            self.input = input_text

            sentence = Sentence(input_text)
            analyzer.analyze(sentence)

            self.assertEqual(1, len(sentence.clauses), "La oración tiene más de una cláusula.")
            clause = sentence.clauses[0]

            self.assertEquals("active", clause.voice)

            #if clause.has_structure("od"):
            #    print "OD: " + str(clause.structure("od").lexical_form())
            if expected_od == "None":
                self.assertTrue(not clause.has_structure("od") or clause.structure("od").is_empty())
            else:
                self.assertEquals(expected_od, clause.structure("od").lexical_form())

            print "OK"

if __name__ == '__main__':
    unittest.main()
