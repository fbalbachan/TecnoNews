#!/usr/bin/env python
#-*- coding: utf-8 -*-
import unittest
from model.sentence import *

class TestVerbs(unittest.TestCase):

    def test_verb_msi(self):
        
        examples = [
            (u'llueve',                    {'person': 0, 'number': u'singular', 'gender': u'neutral'}, u'llover'),

            (u'no hay cupo',               {'person': 3, 'number': u'invariable', 'gender': u'neutral'}, u'haber'),

            (u'el rey juega',              {'person': 3, 'number': u'singular', 'gender': u'neutral'}, u'jugar'),
            (u'el rey ha jugado',          {'person': 3, 'number': u'singular', 'gender': u'neutral'}, u'jugar'),

            (u'los gatos pelean',          {'person': 3, 'number': u'plural', 'gender': u'neutral'}, u'pelear'),
            (u'los gatos han peleado',     {'person': 3, 'number': u'plural', 'gender': u'neutral'}, u'pelear'),

            (u'el rey puede haber jugado', {'person': 3, 'number': u'singular', 'gender': u'neutral'}, u'jugar'),
        ] 

        for (input_text, expected_verb_msi, expected_verb_lemma) in examples:
            sentence = Sentence(input_text)

            verb_msi   = sentence.verb.msi
            verb_lemma = sentence.verb.lemma
            self.assertEqual(expected_verb_msi, verb_msi)
            self.assertEqual(expected_verb_lemma, verb_lemma)

    def test_verb_pass_msi(self):
        
        examples = [
            (u'la cena ha sido servida',     {'person': 3, 'number': u'singular', 'gender': u'neutral'}, u'servir'),
            (u'las cenas han sido servidas', {'person': 3, 'number': u'plural', 'gender': u'neutral'}, u'servir'),

            (u'la batalla fue ganada',       {'person': 3, 'number': u'singular', 'gender': u'neutral'}, u'ganar'),
            (u'las batallas fueron ganadas', {'person': 3, 'number': u'plural', 'gender': u'neutral'}, u'ganar'),

            (u'he sido llamado',     {'person': 1, 'number': u'singular', 'gender': u'neutral'}, u'llamar'),
            (u'hemos sido llamados', {'person': 1, 'number': u'plural', 'gender': u'neutral'}, u'llamar'),
            (u'serás llamado',       {'person': 2, 'number': u'singular', 'gender': u'neutral'}, u'llamar'),
            (u'será llamado',        {'person': 3, 'number': u'singular', 'gender': u'neutral'}, u'llamar'),
            (u'serán llamados',      {'person': 3, 'number': u'plural', 'gender': u'neutral'}, u'llamar'),

        ]

        for (input_text, expected_verb_pass_msi, expected_verb_pass_lemma) in examples:
            sentence = Sentence(input_text)

            verb_pass_msi   = sentence.verb_pass.msi
            verb_pass_lemma = sentence.verb_pass.lemma
            self.assertEqual(expected_verb_pass_msi, verb_pass_msi)
            self.assertEqual(expected_verb_pass_lemma, verb_pass_lemma)


if __name__ == '__main__':
    unittest.main()
