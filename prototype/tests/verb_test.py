#!/usr/bin/env python
#-*- coding: utf-8 -*-
import unittest

from src.model.sentence.sentenceAnalyzer import SentenceAnalyzer
from src.model.sentence.sentence import Sentence
from tests.freelingTreeRepository import FreelingTreeRepository


class TestVerbs(unittest.TestCase):

    def setUp(self):
        self.analyzer = SentenceAnalyzer(FreelingTreeRepository("tests/input/trees"))

    def test_verb_msi_for_modal_verbs(self):
        examples = [('puedes comprar',     {'person': 2, 'number': 'singular', 'gender': 'neutral'}, 'comprar'),
                    ('has podido comprar', {'person': 2, 'number': 'singular', 'gender': 'neutral'}, 'comprar'),]

        for (input_text, expected_verb_msi, expected_verb_lemma) in examples:
            print "trying: %s .. " % input_text,

            sentence = Sentence(input_text)
            self.analyzer.analyze(sentence)

            self.assertEqual(1, len(sentence.clauses), "La oración tiene más de una cláusula.")
            clause = sentence.clauses[0]

            verb_msi   = clause.structure("verb").msi()
            self.assert_is_included(expected_verb_msi, verb_msi)

            verb_lemma = clause.structure("verb").entity().lemma()
            self.assertEqual(expected_verb_lemma, verb_lemma)

            print "OK"

    def test_verb_msi(self):
        examples = [
            #('llueve',                     {'person': 0, 'number': 'singular', 'gender': 'neutral'},    'llover'),
            #('no hay cupo',                {'person': 3, 'number': 'invariable', 'gender': 'neutral'},  'haber'),

            ('el rey juega',               {'person': 3, 'number': 'singular', 'gender': 'neutral'},    'jugar'),
            ('el rey ha jugado',           {'person': 3, 'number': 'singular', 'gender': 'neutral'},    'jugar'),

            ('los gatos pelean',           {'person': 3, 'number': 'plural', 'gender': 'neutral'},      'pelear'),
            ('los gatos han peleado',      {'person': 3, 'number': 'plural', 'gender': 'neutral'},      'pelear'),

            ('el rey puede haber jugado',  {'person': 3, 'number': 'singular', 'gender': 'neutral'},    'jugar'),
        ]

        for (input_text, expected_verb_msi, expected_verb_lemma) in examples:
            print "trying: %s .. " % input_text,
            sentence = Sentence(input_text)
            self.analyzer.analyze(sentence)

            self.assertEqual(1, len(sentence.clauses), "La oración tiene más de una cláusula.")
            clause = sentence.clauses[0]

            verb   = clause.structure("verb").entity()

            self.assert_is_included(expected_verb_msi, verb.msi)
            self.assertEqual(expected_verb_lemma, verb.lemma())

    def test_verb_pass_msi(self):

        examples = [
            ('la cena ha sido servida',     {'person': 3, 'number': 'singular', 'gender': 'feminine'},  'servir'),
            ('las cenas han sido servidas', {'person': 3, 'number': 'plural', 'gender': 'feminine'},    'servir'),

            ('la batalla fue ganada',       {'person': 3, 'number': 'singular', 'gender': 'feminine'},  'ganar'),
            ('las batallas fueron ganadas', {'person': 3, 'number': 'plural', 'gender': 'feminine'},    'ganar'),

            ('he sido llamado',     {'person': 1, 'number': 'singular', 'gender': 'masculine'},  'llamar'),
            ('hemos sido llamados', {'person': 1, 'number': 'plural', 'gender': 'masculine'},    'llamar'),

            ('serás llamado',       {'person': 2, 'number': 'singular', 'gender': 'masculine'},  'llamar'),
            ('seréis llamados',     {'person': 2, 'number': 'plural', 'gender': 'masculine'},  'llamar'),

            ('será llamado',        {'person': 3, 'number': 'singular', 'gender': 'masculine'},  'llamar'),
            ('serán llamados',      {'person': 3, 'number': 'plural', 'gender': 'masculine'},    'llamar'),

        ]

        for (input_text, expected_verb_pass_msi, expected_verb_pass_lemma) in examples:
            print "trying: %s .. " % input_text,
            sentence = Sentence(input_text)
            self.analyzer.analyze(sentence)

            self.assertEqual(1, len(sentence.clauses), "La oración tiene más de una cláusula.")
            clause = sentence.clauses[0]

            verb   = clause.structure("verb").entity()

            self.assertEqual("passive", verb.voice)

            self.assert_is_included(expected_verb_pass_msi, verb.msi)
            self.assertEqual(expected_verb_pass_lemma, verb.lemma())

            print "OK"

    def assert_is_included(self, this, into_that):
        for attribute, value in this.items():
            self.assertTrue(attribute in into_that)
            self.assertEqual(value, into_that[attribute])

if __name__ == '__main__':
    unittest.main()
