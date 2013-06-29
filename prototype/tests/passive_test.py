#!/usr/bin/env python
#-*- coding: utf-8 -*-
import unittest
from model.sentence import *

class TestPassiveSentence(unittest.TestCase):

    def test_verb(self):
        examples = [
            (u'el alimento fue comido por los animales', u'comer', u'los animales', u'el alimento'),
        ]

        for (input_text, expected_verb_lemma, expected_subject, expected_od) in examples:
            sentence = Sentence(input_text)
            print sentence

            self.assertEqual(expected_verb_lemma.__str__(), sentence.verb.lemma.__str__())
            self.assertEqual(expected_subject.__str__(), sentence.subject.__str__())
            self.assertEqual(expected_od.__str__(), sentence.od.__str__())

if __name__ == '__main__':
    unittest.main()
