#!/usr/bin/env python
#-*- coding: utf-8 -*-
import unittest

from src.model.freelingSentenceAnalyzer import FreelingSentenceAnalyzer
from src.model.sentence import Sentence
from tests.freelingTreeRepository import FreelingTreeRepository


class TestWord(unittest.TestCase):

    def setUp(self):
        self.analyzer = FreelingSentenceAnalyzer(FreelingTreeRepository("tests/input/trees"))

    def test_get_all_words_from_sentence(self):

        input_text = 'el Primer Ministro declaró el estado de sitio'

        print "trying: %s .. " % input_text,
        sentence = Sentence(input_text)
        self.analyzer.analyze(sentence)

        self.assertEqual(1, len(sentence.clauses), "La oración tiene más de una cláusula.")
        clause = sentence.clauses[0]

        expected = [
            ('el',              'el',              'DA0MS0'),
            ('Primer_Ministro', 'primer_ministro', 'NP00000'),
            ('declaró',         'declarar',        'VMIS3S0'),
            ('el',              'el',              'DA0MS0'),
            ('estado',          'estado',          'NCMS000'),
            ('de',              'de',              'SPS00'),
            ('sitio',           'sitio',           'NCMS000'),
        ]

        for ((expected_form, expected_lemma, expected_tag), result_word) in zip(expected, clause.proper_leaves()):
            self.assertEqual(expected_form,     result_word.lexical_form)
            self.assertEqual(expected_lemma,    result_word.lemma)
            #self.assertEqual(expected_tag,      result_word.tag)

        print "OK"

    def test_get_words_from_structure(self):

        input_text = 'el Primer Ministro declaró el estado de sitio'

        print "trying: %s .. " % input_text,

        sentence = Sentence(input_text)
        self.analyzer.analyze(sentence)

        self.assertEqual(1, len(sentence.clauses), "La oración tiene más de una cláusula.")
        clause = sentence.clauses[0]

        entity_primer_ministro = filter(lambda e: str(e) == 'el Primer_Ministro', clause.entities)[0]
        primer_ministro_words = entity_primer_ministro.leaves()

        self.assertEqual('el', primer_ministro_words[0].lexical_form)
        self.assertEqual('Primer_Ministro', primer_ministro_words[1].lexical_form)

        print "OK"

if __name__ == '__main__':
    unittest.main()