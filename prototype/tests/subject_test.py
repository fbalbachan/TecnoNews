#!/usr/bin/env python
#-*- coding: utf-8 -*-
import unittest
from model.sentence import *

class TestSubject(unittest.TestCase):

# si activa:
#     1) sujeto a mismo nivel que el verbo
#     candidatos, en orden de preferencia:
#       * a izq, al mismo nivel, a distancia infinita
#         condición: mismo msi que el verbo
#       * a der, al mismo nivel, a distancia 2
#              x y z
#              y a distancia 1 de x
#              z a distancia 2 de x
#       * si lo anterior no funciona, es tácito. hay que expresarlo, a partir del msi del verbo
# else:
#     pass

    def test_subject(self):
        examples = [
            (u'todas las noches viene el cartero', {'person': 3, 'number': u'singular', 'gender': u'neutral'}, u'el cartero'),
            (u'golpeó mucho a su esposa',          {'person': 3, 'number': u'singular', 'gender': u'neutral'}, u'él'),
            (u'me gustó caminar por el bosque',    {'person': 3, 'number': u'singular', 'gender': u'neutral'}, u'caminar por el bosque'),
            (u'llovió toda la noche',              {'person': 0, 'number': u'singular', 'gender': u'neutral'}, None),
            (u'vos y yo comemos pizza',            {'person': 1, 'number': u'plural', 'gender': u'neutral'}, u'vos y yo'),
        ]

        for (input_text, expected_subject, expected_verb_msi) in examples:
            sentence = Sentence(input_text)
            verb_msi = sentence.verb.msi
            subject = sentence.get_subject()
            self.assertEqual(expected_subject, subject)
            self.assertEqual(expected_verb_msi, verb_msi)
