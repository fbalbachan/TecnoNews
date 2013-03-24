#!/usr/bin/env python
#-*- coding: utf-8 -*-
import unittest
from model.sentence import *

class TestSentence(unittest.TestCase):

    def setUp(self):
        sentence = u'el cartero trae las cartas.'
        self.sentence = Sentence(sentence)

    def test_get_entities(self):
        result = self.sentence.entities
        self.assertEqual(result[0].__str__(), u'el cartero')
        self.assertEqual(result[1].__str__(), u'las cartas')

    def test_get_entity_heads(self):
        result = self.sentence.get_entities()
        self.assertEqual(result[0].head.__repr__(), u'n-ms (8,10) cartero [3]')
        self.assertEqual(result[1].head.__repr__(), u'n-fp (23,25) cartas [3]')
        self.assertEqual(result[0].head.__str__(), u'cartero')
        self.assertEqual(result[1].head.__str__(), u'cartas')

    def test_get_entity_head_MSIs(self):
        result = self.sentence.get_entities()
        self.assertEqual(result[0].msi, {'category': u'nombre',
                                         'semantic_classification': None,
                                         'grade': None,
                                         'gender': u'masculino',
                                         'number': u'singular',
                                         'type': u'comun'})
        self.assertEqual(result[1].filtered_msi, {'person': 3,
                                                  'number': u'plural',
                                                  'gender': u'femenino'})


if __name__ == '__main__':
    unittest.main()
