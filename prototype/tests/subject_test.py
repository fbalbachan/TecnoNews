#!/usr/bin/env python
#-*- coding: utf-8 -*-
import unittest
from model.sentence import *

class TestSubject(unittest.TestCase):

    def test_entities_at_verb_level(self):
        examples = [
            (u'todas las noches viene el cartero',      [u'todas las noches', u'el cartero']),
            (u'las cartas del cartero llegaron tarde',  [u'las cartas de el cartero']),
            (u'el golpeador golpeó mucho a su esposa',  [u'el golpeador']),
        ]

        for (input_text, expected_entities) in examples:
            sentence = Sentence(input_text)
            entities_at_verb_level = [e.__str__() for e in sentence.entities_at_verb_level]
            self.assertEqual(expected_entities, entities_at_verb_level)

    def _subject(self):
        examples = [
            (u'todas las noches viene el cartero', {'person': 3, 'number': u'singular', 'gender': u'neutral'},  u'el cartero'),
            (u'golpeó mucho a su esposa',          {'person': 3, 'number': u'singular', 'gender': u'neutral'},  u'él'),
            (u'me gustó caminar por el bosque',    {'person': 3, 'number': u'singular', 'gender': u'neutral'},  u'caminar por el bosque'),
            (u'llovió toda la noche',              {'person': 0, 'number': u'singular', 'gender': u'neutral'},  None),
            (u'vos y yo comemos pizza',            {'person': 1, 'number': u'plural', 'gender': u'neutral'},    u'vos y yo'),
        ]

        for (input_text, expected_subject, expected_verb_msi) in examples:
            sentence = Sentence(input_text)

            subject = sentence.subject
            self.assertEqual(expected_subject, subject)

            verb_msi = sentence.verb.msi
            self.assertEqual(expected_verb_msi, verb_msi)

if __name__ == '__main__':
    unittest.main()