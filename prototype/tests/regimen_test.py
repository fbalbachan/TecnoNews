#!/usr/bin/env python
#-*- coding: utf-8 -*-
import unittest
from model.sentence import *

class TestRegimen(unittest.TestCase):

    def setUp(self):
        self.input_texts_with_regimen = [
                (u'todos los cuatrimestres yo lidio con mis alumnos', u'mis alumnos'),
             ]

    def test_get_regimen(self):
        for (input_text, expected_regimen) in self.input_texts_with_regimen:
            sentence = Sentence(input_text)
            result_regimen = sentence.regimen.__str__()

            print "input: ", input_text
            print "expected: ", expected_regimen
            print "got: ", result_regimen
            print sentence.evidence
            
            self.assertTrue(sentence.is_active)
            self.assertEquals(expected_regimen.encode('utf-8'), sentence.regimen.__str__())


if __name__ == '__main__':
    unittest.main()
