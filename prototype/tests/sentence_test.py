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

        sentence3 = u'el perro y el gato pelearon.'
        self.sentence3 = Sentence(sentence3)

        sentence4 = u'Fulano es malo.'
        self.sentence4 = Sentence(sentence4)

    def test_get_entities(self):
        result = self.sentence1.entities
        self.assertEqual(result[0].__str__(), u'el cartero')
        self.assertEqual(result[1].__str__(), u'las cartas')

        result = self.sentence2.entities
        self.assertEqual(result[0].__str__(), u'el Papa_Francisco')
        self.assertEqual(result[1].__str__(), u'su homilía')

        result = self.sentence3.entities
        self.assertEqual(result[0].__str__(), u'el perro')
        self.assertEqual(result[1].__str__(), u'el perro y el gato')
        self.assertEqual(result[2].__str__(), u'el gato')

    def test_get_entity_head_MSIs(self):
        result = self.sentence1.get_entities()
        self.assertEqual(result[1].msi, {'person': 3,
                                         'number': u'plural',
                                         'gender': u'feminine'})

        result = self.sentence2.get_entities()
        self.assertEqual(result[1].msi, {'person': 3,
                                         'number': u'singular',
                                         'gender': u'feminine'})

        result = self.sentence3.get_entities()
        self.assertEqual(result[1].msi, {'person': 3,
                                         'number': u'plural',
                                         'gender': u'masculine'})

    def test_get_equative_entities(self):
        result = self.sentence4.equative_entities
        self.assertEqual(result[0].__str__(), u'malo')


if __name__ == '__main__':
    unittest.main()
