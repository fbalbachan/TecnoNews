#!/usr/bin/env python
#-*- coding: utf-8 -*-
import unittest

from src.model.freelingSentenceAnalyzer import FreelingSentenceAnalyzer
from src.model.sentence import Sentence
from tests.csv_file_reader import load_csv_test_file
from tests.freelingTreeRepository import FreelingTreeRepository


class TestSubject(unittest.TestCase):

    def setUp(self):
        self.input_texts = load_csv_test_file('tests/input/subject_test.csv')
        self.input_texts_with_msi = load_csv_test_file('tests/input/subject_with_msi_test.csv')
        self.analyzer = FreelingSentenceAnalyzer(FreelingTreeRepository("tests/input/trees"))

    def test_entities_at_verb_level(self):
        examples = [
            ('todas las noches viene el cartero',      ['todas las noches', 'el cartero']),
            ('las cartas del cartero llegaron tarde',  ['las cartas de el cartero']),
            ('el golpeador golpeó mucho a su esposa',  ['el golpeador']),
        ]

        for (input_text, expected_entities) in examples:
            print "trying: %s .. " % input_text,

            sentence = Sentence(input_text)
            self.analyzer.analyze(sentence)

            self.assertEqual(1, len(sentence.clauses), "La oración tiene más de una cláusula.")
            clause = sentence.clauses[0]

            entities_at_verb_level = [ str(entity) for entity in clause.verb_level_entities() ]
            self.assertEqual(expected_entities, entities_at_verb_level)

            print "OK"

    def test_subject_msi(self):
        for (input_text,

             expected_subject_person,
             expected_subject_number,
             expected_subject_gender,
             expected_subject,

             expected_verb_person,
             expected_verb_number,
             expected_verb_gender,
             expected_verb) in self.input_texts_with_msi:

            print "trying: %s .. " % input_text,

            sentence = Sentence(input_text)
            self.analyzer.analyze(sentence)

            self.assertEqual(1, len(sentence.clauses), "La oración tiene más de una cláusula.")
            clause = sentence.clauses[0]

            subject = clause.structure("subject")

            self.assertEqual(int(expected_subject_person), subject.msi()['person'])
            self.assertEqual(expected_subject_number, subject.msi()['number'])
            self.assertEqual(expected_subject_gender, subject.msi()['gender'])
            self.assertEqual(expected_subject, subject.lexical_form())

            verb = clause.structure("verb")

            self.assertEqual(int(expected_verb_person), verb.msi()['person'])
            self.assertEqual(expected_verb_number, verb.msi()['number'])
            self.assertEqual(expected_verb_gender, verb.msi()['gender'])
            self.assertEqual(expected_verb, verb.entity().lemma())

            print "OK"

    def test_subject_active_voice(self):
        for (input_text, expected_subject) in self.input_texts:
            print "trying: %s .. " % input_text,

            sentence = Sentence(input_text)
            self.analyzer.analyze(sentence)

            self.assertEqual(1, len(sentence.clauses), "La oración tiene más de una cláusula.")
            clause = sentence.clauses[0]

            if expected_subject == "None":
                self.assertTrue(not clause.has_structure("subject") or clause.structure("subject").is_empty())
            else:
                self.assertEqual(expected_subject, clause.structure("subject").lexical_form())

            print "OK"

if __name__ == '__main__':
    unittest.main()
