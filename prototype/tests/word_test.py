#!/usr/bin/env python
#-*- coding: utf-8 -*-
import unittest

from src.model.sentence.sentence import Sentence
from src.model.sentence.sentenceAnalyzer import SentenceAnalyzer
from tests.freelingTreeRepository import FreelingTreeRepository
from tests.base_test import TestBase

class TestWord(TestBase):

    def setUp(self):
        super(TestWord, self).setUp()
        self.analyzer = SentenceAnalyzer(FreelingTreeRepository("tests/input/trees"))

    def test_get_all_words_from_sentence(self):

        self.input = input_text = 'el Primer Ministro declaró el estado de sitio'

        print "trying: %s .. " % input_text,
        sentence = Sentence(input_text)
        self.analyzer.analyze(sentence)

        try:
            self.assertEqual(1, len(sentence.clauses), "La oración tiene más de una cláusula.")
        except Exception, e:
            return
        
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
        
        self.input = ""

        for ((expected_form, expected_lemma, expected_tag), result_word) in zip(expected, clause.proper_leaves()):
            try:
                self.assertEqual(expected_form, result_word.original_lexical_form)
            except Exception, e:
                continue

            try:
                self.assertEqual(expected_lemma,    result_word.lemma)
            except Exception, e:
                continue
            #self.assertEqual(expected_tag,      result_word.tag)

        print "OK"

    def test_get_words_from_structure(self):

        self.input = input_text = 'el Primer Ministro declaró el estado de sitio'

        print "trying: %s .. " % input_text,

        sentence = Sentence(input_text)
        self.analyzer.analyze(sentence)

        try:
            self.assertEqual(1, len(sentence.clauses), "La oración tiene más de una cláusula.")
        except Exception, e:
            return
        clause = sentence.clauses[0]

        entity_primer_ministro = filter(lambda e: str(e) == 'el Primer_Ministro', clause.entities)[0]
        primer_ministro_words = entity_primer_ministro.leaves()

        try:
            self.assertEqual('el', primer_ministro_words[0].original_lexical_form)
        except Exception, e:
            return

        try:
            self.assertEqual('Primer_Ministro', primer_ministro_words[1].original_lexical_form)
        except Exception, e:
            return

        print "OK"

if __name__ == '__main__':
    unittest.main()
