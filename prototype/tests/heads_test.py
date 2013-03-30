#!/usr/bin/env python
#-*- coding: utf-8 -*-
import unittest
from model.sentence import *

class TestStructureHead(unittest.TestCase):

    def setUp(self):

        self.data = [
            # (u'la isla desierta',               {'person': 3, 'number': u'singular', 'gender': u'feminine'}),

            # (u'la esquina rosada',              {'person': 3, 'number': u'singular', 'gender': u'feminine'}),
            # (u'el hombre de la esquina rosada', {'person': 3, 'number': u'singular', 'gender': u'masculine'}),

            # (u'las doradas manzanas del sol',      {'person': 3, 'number': u'plural',   'gender': u'feminine'}),
            # (u'el sol sobre las doradas manzanas', {'person': 3, 'number': u'singular', 'gender': u'masculine'}),

            # (u'la selva de los animales',       {'person': 3, 'number': u'singular', 'gender': u'feminine'}),
            # (u'los animales de la selva',       {'person': 3, 'number': u'plural',   'gender': u'masculine'}),

            # (u'los virus',                      {'person': 3, 'number': u'plural',   'gender': u'masculine'}),
            # (u'el virus',                       {'person': 3, 'number': u'singular', 'gender': u'masculine'}),

            # (u'caminar por el bosque',          {'person': 3, 'number': u'singular', 'gender': u'neutral'}),

            # (u'el perro y el gato',           {'person': 3, 'number': u'plural',   'gender': u'masculine'}),
            # (u'Fulano y Mengano',             {'person': 3, 'number': u'plural',   'gender': u'masculine'}),
            # (u'vos y yo',                     {'person': 3, 'number': u'plural',   'gender': u'neutral'}),
            # (u'tú y yo',                      {'person': 3, 'number': u'plural', 'gender': u'neutral'}),
            # (u'la paloma y el águila',        {'person': 3, 'number': u'plural', 'gender': u'feminine'}),
            # (u'la paloma y el perro',        {'person': 3, 'number': u'plural', 'gender': u'masculine'}),
            (u'la paloma y la codorniz',        {'person': 3, 'number': u'plural', 'gender': u'feminine'}),

        ]

        self.grammatical_person_data = [
        (u'yo',        {'person': 1, 'number': u'singular', 'gender': u'neutral'}),
        (u'tú',        {'person': 2, 'number': u'singular', 'gender': u'neutral'}),

        (u'él',        {'person': 3, 'number': u'singular', 'gender': u'masculine'}),
        (u'ella',      {'person': 3, 'number': u'singular', 'gender': u'feminine'}),
        
        (u'ustedes',   {'person': 2, 'number': u'plural', 'gender': u'neutral'}),

        (u'nosotros',  {'person': 1, 'number': u'plural', 'gender': u'masculine'}),
        (u'vosotros',  {'person': 2, 'number': u'plural', 'gender': u'masculine'}),
        (u'ellos',     {'person': 3, 'number': u'plural', 'gender': u'masculine'}),

        (u'nosotras',  {'person': 1, 'number': u'plural', 'gender': u'feminine'}),
        (u'vosotras',  {'person': 2, 'number': u'plural', 'gender': u'feminine'}),
        (u'ellas',     {'person': 3, 'number': u'plural', 'gender': u'feminine'}),
        ]

    def test_get_structure_MSIs(self):
        for (sentence, expected_MSI) in self.data:
            entity = filter(lambda x: x.__str__() == u"la paloma y la codorniz", Sentence(sentence).get_entities())[0]
            print u"trying: %s | result: %s | expected: %s" % (entity, entity.msi, expected_MSI)
            self.assertEqual(entity.msi, expected_MSI)

    def get_grammatical_person_MSIs(self):
        for (sentence, expected_MSI) in self.grammatical_person_data:
            entity = Sentence(sentence).get_entities()[0]
            print u"%s | result: %s | expected: %s" % (entity, entity.msi, expected_MSI)
            # debug: print u"full: %s | label: %s | tag: %s | lemma: %s" % (entity.full_msi, entity.label, entity.words[0].tag, entity.words[0].lemma)
            self.assertEqual(entity.msi, expected_MSI)


if __name__ == '__main__':
    unittest.main()
