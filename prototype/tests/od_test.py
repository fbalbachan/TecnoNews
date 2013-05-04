#!/usr/bin/env python
#-*- coding: utf-8 -*-
import unittest
from model.sentence import *

class TestOD(unittest.TestCase):

    def setUp(self):
        self.sentences = [
            Sentence(s) for s in [
                u'el cartero trae las cartas.'
            ]
        ]

    def test_get_OD(self):
        sentence = self.sentences[0]
        self.assertTrue(sentence.is_active)

        od = sentence.get_OD()
        self.assertEqual(od.__str__(), u'las cartas')


if __name__ == '__main__':
    unittest.main()
