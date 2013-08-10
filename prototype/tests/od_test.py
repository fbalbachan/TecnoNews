#!/usr/bin/env python
#-*- coding: utf-8 -*-
import unittest
from model.sentence import *
from csv_file_reader import load_csv_test_file

class TestOD(unittest.TestCase):

    def setUp(self):
        self.input_texts_with_ods = load_csv_test_file('tests/input/od_test.csv')

    def test_get_OD(self):
        for (input_text, expected_od) in self.input_texts_with_ods:
            sentence = Sentence(input_text)
            result_od = sentence.od.__str__()

            print "input: ", input_text
            print "expected: ", expected_od
            print "got: ", result_od
            print sentence.evidence
            
            self.assertTrue(sentence.is_active)
            self.assertEquals(expected_od.encode('utf-8').strip(), sentence.od.__str__().strip())


if __name__ == '__main__':
    unittest.main()
