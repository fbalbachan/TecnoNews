#!/usr/bin/env python
#-*- coding: utf-8 -*-
import unittest
from model.sentence import *

class TestSubject(unittest.TestCase):

    def test_entity_position(self):
        examples = [
            (u'todas las noches viene el cartero',      u'todas las noches',          (1, 0)),
            (u'todas las noches viene el cartero',      u'el cartero',                (1, 2)),
            (u'las cartas del cartero llegaron tarde',  u'las cartas de el cartero',  (1, 0)),
            (u'las cartas del cartero llegaron tarde',  u'el cartero',                (3, 0)),
        ]

        for (input_text, expected_entity, (expected_level, expected_position)) in examples:
            sentence = Sentence(input_text)
            entity = filter(lambda e: e.__str__() == expected_entity, sentence.entities)[0]
            self.assertEqual(expected_level, entity.level)
            self.assertEqual(expected_position, entity.position)

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