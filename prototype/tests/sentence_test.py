#!/usr/bin/env python
#-*- coding: utf-8 -*-
import unittest
from model.sentence import *

class TestSentence(unittest.TestCase):

    def setUp(self):
        sentence1 = u'el cartero trae las cartas.'
        self.sentence1 = Sentence(sentence1)

        # sentence2 = u'el Papa Francisco prepara su homilía.'
        # self.sentence2 = Sentence(sentence2)

        # sentence3 = u'el perro y el gato pelearon.'
        # self.sentence3 = Sentence(sentence3)

        # sentence4 = u'Fulano es malo.'
        # self.sentence4 = Sentence(sentence4)

        sentence5 = u'las cartas son llevadas por el cartero.'
        self.sentence5 = Sentence(sentence5)

        sentence6 = u'el pozo ha sido vaciado.'
        self.sentence6 = Sentence(sentence6)

        sentence7 = u'él ha sido presidente.'
        self.sentence7 = Sentence(sentence7)

        sentence8 = u'llueve.'
        self.sentence8 = Sentence(sentence8)

        sentence9 = u'está garuando.'
        self.sentence9 = Sentence(sentence9)

    # def test_get_entities(self):
    #     result = self.sentence1.entities
    #     self.assertEqual(result[0].__str__(), u'el cartero')
    #     self.assertEqual(result[1].__str__(), u'las cartas')

    #     result = self.sentence2.entities
    #     self.assertEqual(result[0].__str__(), u'el Papa_Francisco')
    #     self.assertEqual(result[1].__str__(), u'su homilía')

    #     result = self.sentence3.entities
    #     self.assertEqual(result[0].__str__(), u'el perro')
    #     self.assertEqual(result[1].__str__(), u'el perro y el gato')
    #     self.assertEqual(result[2].__str__(), u'el gato')

    # def test_get_entity_head_MSIs(self):
    #     result = self.sentence1.get_entities()
    #     self.assertEqual(result[1].msi, {'person': 3,
    #                                      'number': u'plural',
    #                                      'gender': u'feminine'})

    #     result = self.sentence2.get_entities()
    #     self.assertEqual(result[1].msi, {'person': 3,
    #                                      'number': u'singular',
    #                                      'gender': u'feminine'})

    #     result = self.sentence3.get_entities()
    #     self.assertEqual(result[1].msi, {'person': 3,
    #                                      'number': u'plural',
    #                                      'gender': u'masculine'})

    # def test_get_equative_entities(self):
    #     result = self.sentence4.equative_entities
    #     self.assertEqual(result[0].__str__(), u'malo')

    def test_passive_or_active(self):
        is_active = self.sentence1.is_active
        is_passive = self.sentence1.is_passive
        self.assertTrue(is_active)
        self.assertFalse(is_passive)

        is_active = self.sentence5.is_active
        is_passive = self.sentence5.is_passive
        self.assertFalse(is_active)
        self.assertTrue(is_passive)

        is_active = self.sentence6.is_active
        is_passive = self.sentence6.is_passive
        self.assertFalse(is_active)
        self.assertTrue(is_passive)

        is_active = self.sentence7.is_active
        is_passive = self.sentence7.is_passive
        self.assertTrue(is_active)
        self.assertFalse(is_passive)

        is_active = self.sentence8.is_active
        is_passive = self.sentence8.is_passive
        is_unimember = self.sentence8.is_unimember
        self.assertFalse(is_active)
        self.assertFalse(is_passive)
        self.assertTrue(is_unimember)

        is_active = self.sentence9.is_active
        is_passive = self.sentence9.is_passive
        is_unimember = self.sentence9.is_unimember
        print self.sentence9.freeling_output
        self.assertFalse(is_active)
        self.assertFalse(is_passive)
        self.assertTrue(is_unimember)


if __name__ == '__main__':
    unittest.main()
