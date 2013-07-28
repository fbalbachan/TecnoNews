#!/usr/bin/env python
#-*- coding: utf-8 -*-
import unittest
from model.sentence import *

class TestStructureHead(unittest.TestCase):

    def setUp(self):

        self.data = [
        (u'la isla desierta', u'la isla desierta', {'person':3,'number':u'singular','gender':u'feminine'}),
        (u'la esquina rosada', u'la esquina rosada', {'person':3,'number':u'singular','gender':u'feminine'}),
        (u'el hombre de la esquina rosada', u'el hombre de la esquina rosada', {'person':3,'number':u'singular','gender':u'masculine'}),
        (u'las doradas manzanas del sol', u'las doradas manzanas de el sol', {'person':3,'number':u'plural',   'gender':u'feminine'}),
        (u'el sol sobre las doradas manzanas', u'el sol sobre las doradas manzanas', {'person':3,'number':u'singular','gender':u'masculine'}),
        (u'la selva de los animales', u'la selva de los animales', {'person':3,'number':u'singular','gender':u'feminine'}),
        (u'los animales de la selva', u'los animales de la selva', {'person':3,'number':u'plural',   'gender':u'masculine'}),
        (u'los virus', u'los virus', {'person':3,'number':u'plural',   'gender':u'masculine'}),
        (u'el virus', u'el virus', {'person':3,'number':u'singular','gender':u'masculine'}),
        (u'el perro y el gato', u'el perro y el gato', {'person':3,'number':u'plural','gender':u'masculine'}),
        (u'Fulano y Mengano', u'Fulano y Mengano', {'person':3,'number':u'plural','gender':u'neutral'}), # 'masculine' ?
        (u'vos y yo', u'vos y yo', {'person':1,'number':u'plural','gender':u'neutral'}),
        (u'tú y yo', u'tú y yo', {'person':1,'number':u'plural','gender':u'neutral'}),
        # (u'la paloma y el águila', u'la paloma y el águila', {'person':3,'number':u'plural','gender':u'feminine'}), # coord ?
        (u'la paloma y el perro', u'la paloma y el perro', {'person':3,'number':u'plural','gender':u'masculine'}),
        (u'la paloma y la codorniz', u'la paloma y la codorniz', {'person':3,'number':u'plural','gender':u'feminine'}),
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

    def test_get_entity_MSI(self):
        for (input_text, which_entity, expected_MSI) in self.data:
            entity = filter(lambda e: e.__str__() == which_entity.encode('utf-8'), Sentence(input_text).get_entities())[0]

            print("trying: %s" % entity)
            print("result: %s | expected: %s" % (entity.msi, expected_MSI))

            self.assertEqual(entity.msi, expected_MSI)

    def test_get_grup_verb_inf_MSI(self):
        input_text = u'caminar por el bosque es peligroso' 
        entity = filter(lambda x: x.__str__() == u'caminar por el bosque'.encode('utf-8'), Sentence(input_text).get_entities())[0]
        expected_MSI = {'person': 3, 'number': u'singular', 'gender': u'neutral'}

        print("trying: %s" % entity)
        print("result: %s | expected: %s" % (entity.msi, expected_MSI))

        self.assertEqual(entity.msi, expected_MSI)

    def test_get_grammatical_person_MSIs(self):
        for (sentence, expected_MSI) in self.grammatical_person_data:
            entity = Sentence(sentence).get_entities()[0]

            print("trying: %s" % entity)
            print("%s | result: %s | expected: %s" % (entity, entity.msi, expected_MSI))

            self.assertEqual(entity.msi, expected_MSI)


if __name__ == '__main__':
    unittest.main()
