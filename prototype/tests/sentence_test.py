#!/usr/bin/env python
#-*- coding: utf-8 -*-
import unittest
from model.sentence import *

class TestSentence(unittest.TestCase):

    def setUp(self):
        sentence1 = u'el cartero trae las cartas.'
        self.sentence1 = Sentence(sentence1)

        sentence2 = u'el Papa Francisco prepara su homilía.'
        self.sentence2 = Sentence(sentence2)

    def test_get_entities(self):
        result = self.sentence1.entities
        self.assertEqual(result[0].__str__(), u'el cartero')
        self.assertEqual(result[1].__str__(), u'las cartas')

        result = self.sentence2.entities
        self.assertEqual(result[0].__str__(), u'el Papa_Francisco')
        self.assertEqual(result[1].__str__(), u'su homilía')

    def test_get_entity_heads(self):
        result = self.sentence1.get_entities()
        self.assertEqual(result[0].head.__repr__(), u'n-ms (8,10) cartero [3]')
        self.assertEqual(result[0].head.__str__(), u'cartero')
        self.assertEqual(result[1].head.__repr__(), u'n-fp (23,25) cartas [3]')
        self.assertEqual(result[1].head.__str__(), u'cartas')

        result = self.sentence2.get_entities()
        self.assertEqual(result[0].head.__repr__(), u'w-ms (8,10) Papa_Francisco [3]')
        self.assertEqual(result[0].head.__str__(), u'Papa_Francisco')
        self.assertEqual(result[1].head.__repr__(), u'n-fs (23,25) homilía [3]')
        self.assertEqual(result[1].head.__str__(), u'homilía')

    def test_get_entity_head_MSIs(self):
        result = self.sentence1.get_entities()
        self.assertEqual(result[0].full_msi, {'category': u'noun',
                                              'semantic_classification': None,
                                              'grade': None,
                                              'gender': u'masculine',
                                              'number': u'singular',
                                              'type': u'common'})
        self.assertEqual(result[1].msi, {'person': 3,
                                         'number': u'plural',
                                         'gender': u'feminine'})

        result = self.sentence2.get_entities()
        self.assertEqual(result[0].full_msi, {'category': u'noun',
                                              'semantic_classification': None,
                                              'grade': None,
                                              'gender': None,
                                              'number': None,
                                              'type': u'proper'})
        self.assertEqual(result[1].msi, {'person': 3,
                                         'number': u'singular',
                                         'gender': u'feminine'})


if __name__ == '__main__':
    unittest.main()
