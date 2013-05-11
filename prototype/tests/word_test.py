#!/usr/bin/env python
#-*- coding: utf-8 -*-
import unittest
from model.sentence import *

class TestWord(unittest.TestCase):

    def test_build_a_word(self):
        
        input_text = u'+(Primer_Ministro primer_ministro NP00000 -){2'
        primer_ministro_word = Word(input_text)

        self.assertEqual('Primer_Ministro', primer_ministro_word.form)
        self.assertEqual('primer_ministro', primer_ministro_word.lemma)
        self.assertEqual('NP00000',         primer_ministro_word.tag)        
        self.assertEqual(2,                 primer_ministro_word.position)        

    def test_get_all_words_from_sentence(self):

        input_text = u'el Primer Ministro declaró el estado de sitio'
        sentence = Sentence(input_text)

        expected = [
            (u'el',              u'el',              'DA0MS0',  1),
            (u'Primer_Ministro', u'primer_ministro', 'NP00000', 2),
            (u'declaró',         u'declarar',        'VMIS3S0', 3),
            (u'el',              u'el',              'DA0MS0',  4),
            (u'estado',          u'estado',          'NCMS000', 5),
            (u'de',              u'de',              'SPS00',   6),
            (u'sitio',           u'sitio',           'NCMS000', 7),
        ]

        for ((expected_form, expected_lemma, expected_tag, expected_position), result_word) in zip(expected, sentence.all_words):
            self.assertEqual(expected_form,     result_word.form)
            self.assertEqual(expected_lemma,    result_word.lemma)
            self.assertEqual(expected_tag,      result_word.tag)
            self.assertEqual(expected_position, result_word.position)

    def test_get_words_from_structure(self):
        
        input_text = u'el Primer Ministro declaró el estado de sitio'
        sentence = Sentence(input_text)
        
        primer_ministro_structure = filter(lambda e: e.__str__() == 'el Primer_Ministro', sentence.get_entities())[0]
        primer_ministro_words = primer_ministro_structure.words

        self.assertEqual(u'el', primer_ministro_words[0].form)        
        self.assertEqual(1, primer_ministro_words[0].position)        

        self.assertEqual(u'Primer_Ministro', primer_ministro_words[1].form)
        self.assertEqual(2, primer_ministro_words[1].position)


if __name__ == '__main__':
    unittest.main()