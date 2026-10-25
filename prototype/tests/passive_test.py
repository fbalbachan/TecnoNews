#!/usr/bin/env python
#-*- coding: utf-8 -*-
import unittest

from tests.csv_file_reader import load_csv_test_file
from src.model.sentence.sentenceAnalyzer import SentenceAnalyzer
from src.model.sentence.sentence import Sentence
from tests.freelingTreeRepository import FreelingTreeRepository
from tests.base_test import TestBase

class TestPassiveSentence(TestBase):

    def setUp(self):
        super(TestPassiveSentence, self).setUp()
        self.input_texts = load_csv_test_file('tests/input/passive_test.csv')

    def test_verb(self):
        analyzer = SentenceAnalyzer(FreelingTreeRepository("tests/input/trees"))

        for (input_text, expected_verb_lemma, expected_subject, expected_od) in self.input_texts:
            print("trying: %s .. " % input_text, end=' ')

            self.input = input_text

            sentence = Sentence(input_text)
            analyzer.analyze(sentence)

            self.assertEqual(1, len(sentence.clauses), "La oración tiene más de una cláusula.")

            clause = sentence.clauses[0]

            self.assertEqual(expected_subject, clause.structure("subject").lexical_form())
            self.assertEqual(expected_verb_lemma, clause.structure("verb").entity().lemma())

            self.assertEqual(expected_od, clause.structure("od").lexical_form())

            print("OK")

if __name__ == '__main__':
    unittest.main()
