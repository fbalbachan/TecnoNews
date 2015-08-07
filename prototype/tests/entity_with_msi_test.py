#!/usr/bin/env python
#-*- coding: utf-8 -*-
import unittest

from src.model.sentence.sentence import Sentence
from src.model.sentence.sentenceAnalyzer import SentenceAnalyzer
from tests.freelingTreeRepository import FreelingTreeRepository
from src.ling.gender import Gender
from src.ling.number import Number

class TestStructureHead(unittest.TestCase):

    def setUp(self):
        self.analyzer = SentenceAnalyzer(FreelingTreeRepository("tests/input/trees"))

        self.data = [
        ('la isla desierta', 'la isla desierta',
         {'person':3,'number': Number.singular, 'gender': Gender.feminine}),
        ('la esquina rosada', 'la esquina rosada',
         {'person':3,'number': Number.singular, 'gender':Gender.feminine}),
        ('el hombre de la esquina rosada', 'el hombre de la esquina rosada',
         {'person':3,'number': Number.singular, 'gender':Gender.masculine}),
        ('las doradas manzanas del sol', 'las doradas manzanas de el sol',
         {'person':3,'number': Number.plural,   'gender': Gender.feminine}),
        ('el sol sobre las doradas manzanas', 'el sol sobre las doradas manzanas',
         {'person':3, 'number': Number.singular, 'gender': Gender.masculine}),
        ('la selva de los animales', 'la selva de los animales',
         {'person': 3, 'number': Number.singular, 'gender':Gender.feminine}),
        ('los animales de la selva', 'los animales de la selva',
         {'person': 3, 'number': Number.plural, 'gender': Gender.masculine}),
        #('los virus', 'los virus', {'person':3,'number': Number.plural,   'gender':Gender.masculine}),
        #('el virus', 'el virus', {'person':3,'number': Number.singular, 'gender': Gender.masculine}),
        ('el perro y el gato', 'el perro y el gato', {'person':3,'number': Number.plural,'gender':Gender.masculine}),
        ('Fulano y Mengano', 'Fulano y Mengano', {'person':3,'number': Number.plural,'gender': Gender.neutral}), # Gender.masculine ?
        ('vos y yo', 'vos y yo', {'person':1,'number': Number.plural,'gender': Gender.neutral}),
        ('tú y yo', 'tú y yo', {'person':1,'number': Number.plural,'gender': Gender.neutral}),
        # ('la paloma y el águila', 'la paloma y el águila', {'person':3,'number': Number.plural,'gender':Gender.feminine}), # coord ?
        ('la paloma y el perro', 'la paloma y el perro', {'person':3,'number': Number.plural,'gender':Gender.masculine}),
        ('la paloma y la codorniz', 'la paloma y la codorniz', {'person':3,'number': Number.plural,'gender':Gender.feminine}),
        ]

        self.grammatical_person_data = [
            ('yo',        {'person': 1, 'number': Number.singular, 'gender': Gender.neutral}),
            ('tú',        {'person': 2, 'number': Number.singular, 'gender': Gender.neutral}),

            ('él',        {'person': 3, 'number': Number.singular, 'gender': Gender.masculine}),
            ('ella',      {'person': 3, 'number': Number.singular, 'gender': Gender.feminine}),

            ('ustedes',   {'person': 3, 'number': Number.plural, 'gender': Gender.masculine}),

            ('nosotros',  {'person': 1, 'number': Number.plural, 'gender': Gender.masculine}),
            ('vosotros',  {'person': 2, 'number': Number.plural, 'gender': Gender.masculine}),
            ('ellos',     {'person': 3, 'number': Number.plural, 'gender': Gender.masculine}),

            ('nosotras',  {'person': 1, 'number': Number.plural, 'gender': Gender.feminine}),
            ('vosotras',  {'person': 2, 'number': Number.plural, 'gender': Gender.feminine}),
            ('ellas',     {'person': 3, 'number': Number.plural, 'gender': Gender.feminine}), ]

    def test_get_entity_MSI(self):
        for (input_text, which_entity, expected_MSI) in self.data:
            sentence = Sentence(input_text)
            self.analyzer.analyze(sentence)

            self.assertEqual(1, len(sentence.clauses), "La oración tiene más de una cláusula.")
            clause = sentence.clauses[0]

            entity = filter(lambda e: str(e) == which_entity, clause.entities)[0]

            print ("trying: %s" % entity), "..",

            self.assert_is_included(expected_MSI, entity.msi)
            print "OK"

    def test_get_grup_verb_inf_MSI(self):
        input_text = 'caminar por el bosque es peligroso'
        sentence = Sentence(input_text)
        self.analyzer.analyze(sentence)

        self.assertEqual(1, len(sentence.clauses), "La oración tiene más de una cláusula.")
        clause = sentence.clauses[0]

        entity = filter(lambda x: str(x) == 'caminar por el bosque'.encode('utf-8'), clause.entities)[0]
        expected_MSI = {'person': 3, 'number': Number.singular, 'gender': None}

        print ("trying: %s" % entity), "..",

        self.assert_is_included(expected_MSI, entity.msi)
        print "OK"

    def test_get_grammatical_person_MSIs(self):
        for (input_text, expected_MSI) in self.grammatical_person_data:
            sentence = Sentence(input_text)
            self.analyzer.analyze(sentence)

            self.assertEqual(1, len(sentence.clauses), "La oración tiene más de una cláusula.")
            clause = sentence.clauses[0]

            entity = clause.entities[0]

            print ("trying: %s" % entity), "..",

            self.assert_is_included(expected_MSI, entity.msi)
            print "OK"

    def assert_is_included(self, this, into_that):
        for attribute, value in this.items():
            self.assertTrue(attribute in into_that)
            self.assertEqual(value, into_that[attribute])

if __name__ == '__main__':
    unittest.main()
