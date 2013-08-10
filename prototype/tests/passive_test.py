#!/usr/bin/env python
#-*- coding: utf-8 -*-
import unittest
from model.sentence import *
from csv_file_reader import load_csv_test_file

class TestPassiveSentence(unittest.TestCase):

    def setUp(self):
        self.input_texts = load_csv_test_file('tests/input/passive_test.csv')

    def test_verb(self):
        for (input_text, expected_verb_lemma, expected_subject, expected_od) in self.input_texts:
            sentence = Sentence(input_text)

            self.assertEqual(expected_subject.__str__(), sentence.subject.__str__())
            self.assertEqual(expected_verb_lemma.__str__(), sentence.verb.lemma.__str__())
            self.assertEqual(expected_od.__str__(), sentence.od.__str__())

if __name__ == '__main__':
    unittest.main()
