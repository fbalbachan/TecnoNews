#!/usr/bin/env python
#-*- coding: utf-8 -*-
import unittest
from model.sentence import *

class TestEquative(unittest.TestCase):

    def setUp(self):
        self.input_texts_with_equative = [
            (u'Fulano es malo', u'malo'),
            (u'Fulano me parece una buena persona', u'una buena persona'),
            (u'Fulano parece huraño y taciturno', u'huraño y taciturno'),

        ]

    def test_get_equative(self):
        for (input_text, expected_equative) in self.input_texts_with_equative:
            sentence = Sentence(input_text)
            print sentence

            result_equative = sentence.equative.__str__()
            
            print "input: ", input_text
            print "expected: ", expected_equative
            print "got: ", result_equative
            print sentence.evidence

            self.assertTrue(sentence.is_active)
            self.assertEquals(expected_equative.encode('utf-8'), sentence.equative.__str__())


if __name__ == '__main__':
    unittest.main()
