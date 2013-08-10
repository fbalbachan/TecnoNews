#!/usr/bin/env python
#-*- coding: utf-8 -*-
import unittest
from model.sentence import *

class TestObjects(unittest.TestCase):

    def test_od(self):
        examples = [
            (u'el cartero trajo las cartas',  u'las cartas'),
            (u'el perro comió carne',  u'carne'),
            (u'las águilas cazaron palomas',  u'palomas'),
        ]

        for (input_text, expected_od) in examples:
            sentence = Sentence(input_text)
            print "sujeto:", sentence.subject
            print "objeto:", sentence.od
            self.assertEqual(expected_od, sentence.od.__str__())


if __name__ == '__main__':
    unittest.main()
