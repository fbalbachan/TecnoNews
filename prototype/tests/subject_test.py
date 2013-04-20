#!/usr/bin/env python
#-*- coding: utf-8 -*-
import unittest
from model.sentence import *

class TestSubject(unittest.TestCase):

    def _entities_at_verb_level(self):
        examples = [
            (u'todas las noches viene el cartero',      [u'todas las noches', u'el cartero']),
            (u'las cartas del cartero llegaron tarde',  [u'las cartas de el cartero']),
            (u'el golpeador golpeó mucho a su esposa',  [u'el golpeador']),
        ]

        for (input_text, expected_entities) in examples:
            sentence = Sentence(input_text)
            entities_at_verb_level = [e.__str__() for e in sentence.entities_at_verb_level]
            self.assertEqual(expected_entities, entities_at_verb_level)

    def test_subject(self):
        examples = [
            (u'todas las noches viene el cartero',
             {'person': 3, 'number': u'singular', 'gender': u'neutral'},
             u'el cartero',
             {'person': 3, 'number': u'singular', 'gender': u'neutral'},
             u'venir'),

            (u'golpeó mucho a su esposa',
             {'person': 3, 'number': u'singular', 'gender': u'neutral'},
             u'él',
             {'person': 3, 'number': u'singular', 'gender': u'neutral'},
             u'golpear'),

            (u'me gustó caminar por el bosque',
             {'person': 3, 'number': u'singular', 'gender': u'neutral'},
             u'caminar por el bosque',
             {'person': 3, 'number': u'singular', 'gender': u'neutral'},
             u'gustart',
            ),

            (u'llovió toda la noche',
             {'person': 0, 'number': u'singular', 'gender': u'neutral'},
             'None',
             {'person': 0, 'number': u'singular', 'gender': u'neutral'},
             u'llover'),

            (u'vos y yo comemos pizza',
             {'person': 1, 'number': u'plural', 'gender': u'neutral'},
             u'vos y yo',
             {'person': 1, 'number': u'plural', 'gender': u'neutral'},
             u'comer'),
        ]

        for (input_text,
             expected_subject_msi,
             expected_subject,
             expected_verb_msi,
             expected_verb) in examples:

            sentence = Sentence(input_text)

            subject = sentence.subject
            self.assertEqual(expected_subject, subject.__str__())

            verb_msi = sentence.verb.msi
            self.assertEqual(expected_verb_msi, verb_msi)

if __name__ == '__main__':
    unittest.main()
