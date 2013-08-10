#!/usr/bin/env python
#-*- coding: utf-8 -*-
import unittest
from model.sentence import *
from csv_file_reader import load_csv_test_file

class TestSentence(unittest.TestCase):

    def setUp(self):
        self.input_texts = load_csv_test_file('tests/input/sentence_test.csv')

    def test_passive_or_active(self):
        for (input_text, active, passive, unimember) in self.input_texts:
            sentence = Sentence(input_text)
            is_active = active == 'True'
            is_passive = passive == 'True'
            is_unimember = unimember == 'True'

            print "trying: ", sentence

            self.assertEquals(is_unimember, sentence.is_unimember)
            self.assertEquals(is_active, sentence.is_active)
            self.assertEquals(is_passive, sentence.is_passive)


if __name__ == '__main__':
    unittest.main()
