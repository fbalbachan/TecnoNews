#!/usr/bin/env python
#-*- coding: utf-8 -*-
import unittest
from model.sentence import *

class TestObjects(unittest.TestCase):

    def test_OD(self):
        examples = [
            (u'el cartero trajo las cartas',  u'las cartas'),
            (u'el perro comió carne',  u'carne'),
            (u'las águilas cazaron palomas',  u'palomas'),
        ]

        for (input_text, expected_OD) in examples:
            sentence = Sentence(input_text)
            print "sujeto:", sentence.subject
            self.assertEqual(expected_OD, sentence.OD.__str__())


if __name__ == '__main__':
    unittest.main()
