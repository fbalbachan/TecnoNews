#!/usr/bin/env python
#-*- coding: utf-8 -*-
import unittest
from model.sentence import *

class TestVerbs(unittest.TestCase):

    def test_verb_msi(self):
        
        examples = [
            (u'el rey juega',              {'person': 3, 'number': u'singular', 'gender': u'neutral'}, u'jugar'),
            (u'el rey ha jugado',          {'person': 3, 'number': u'singular', 'gender': u'neutral'}, u'jugar'),
            (u'el rey puede haber jugado', {'person': 3, 'number': u'singular', 'gender': u'neutral'}, u'jugar'),
        ] 

        for (input_text, expected_verb_msi, expected_verb_lemma) in examples:
            sentence = Sentence(input_text)

            verb_msi   = sentence.verbs[0].msi
            verb_lemma = sentence.verbs[0].lemma
            self.assertEqual(expected_verb_msi, verb_msi)
            self.assertEqual(expected_verb_lemma, verb_lemma)

        # for x in sentence.verbs: print "verbo: ", x, x.label, x.msi, x.lemma

                
if __name__ == '__main__':
    unittest.main()
