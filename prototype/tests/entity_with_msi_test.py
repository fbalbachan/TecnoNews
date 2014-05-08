#!/usr/bin/env python
#-*- coding: utf-8 -*-
import unittest

from src.model.sentence.sentenceAnalyzer import SentenceAnalyzer
from src.model.sentence.sentence import Sentence
from tests.freelingTreeRepository import FreelingTreeRepository


class TestStructureHead(unittest.TestCase):

    def setUp(self):
        self.analyzer = SentenceAnalyzer(FreelingTreeRepository("tests/input/trees"))

        self.data = [
        ('la isla desierta', 'la isla desierta', {'person':3,'number':'singular','gender':'feminine'}),
        ('la esquina rosada', 'la esquina rosada', {'person':3,'number':'singular','gender':'feminine'}),
        ('el hombre de la esquina rosada', 'el hombre de la esquina rosada', {'person':3,'number':'singular','gender':'masculine'}),
        ('las doradas manzanas del sol', 'las doradas manzanas de el sol', {'person':3,'number':'plural',   'gender':'feminine'}),
        ('el sol sobre las doradas manzanas', 'el sol sobre las doradas manzanas', {'person':3,'number':'singular','gender':'masculine'}),
        ('la selva de los animales', 'la selva de los animales', {'person':3,'number':'singular','gender':'feminine'}),
        ('los animales de la selva', 'los animales de la selva', {'person':3,'number':'plural',   'gender':'masculine'}),
        #('los virus', 'los virus', {'person':3,'number':'plural',   'gender':'masculine'}),
        #('el virus', 'el virus', {'person':3,'number':'singular','gender':'masculine'}),
        ('el perro y el gato', 'el perro y el gato', {'person':3,'number':'plural','gender':'masculine'}),
        ('Fulano y Mengano', 'Fulano y Mengano', {'person':3,'number':'plural','gender':'neutral'}), # 'masculine' ?
        ('vos y yo', 'vos y yo', {'person':1,'number':'plural','gender':'neutral'}),
        ('tú y yo', 'tú y yo', {'person':1,'number':'plural','gender':'neutral'}),
        # ('la paloma y el águila', 'la paloma y el águila', {'person':3,'number':'plural','gender':'feminine'}), # coord ?
        ('la paloma y el perro', 'la paloma y el perro', {'person':3,'number':'plural','gender':'masculine'}),
        ('la paloma y la codorniz', 'la paloma y la codorniz', {'person':3,'number':'plural','gender':'feminine'}),
        ]

        self.grammatical_person_data = [
        ('yo',        {'person': 1, 'number': 'singular', 'gender': 'neutral'}),
        ('tú',        {'person': 2, 'number': 'singular', 'gender': 'neutral'}),

        ('él',        {'person': 3, 'number': 'singular', 'gender': 'masculine'}),
        ('ella',      {'person': 3, 'number': 'singular', 'gender': 'feminine'}),

        ('ustedes',   {'person': 2, 'number': 'plural', 'gender': 'neutral'}),

        ('nosotros',  {'person': 1, 'number': 'plural', 'gender': 'masculine'}),
        ('vosotros',  {'person': 2, 'number': 'plural', 'gender': 'masculine'}),
        ('ellos',     {'person': 3, 'number': 'plural', 'gender': 'masculine'}),

        ('nosotras',  {'person': 1, 'number': 'plural', 'gender': 'feminine'}),
        ('vosotras',  {'person': 2, 'number': 'plural', 'gender': 'feminine'}),
        ('ellas',     {'person': 3, 'number': 'plural', 'gender': 'feminine'}),
        ]

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
        expected_MSI = {'person': 3, 'number': 'singular', 'gender': 'neutral'}

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
