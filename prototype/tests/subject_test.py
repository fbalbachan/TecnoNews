#!/usr/bin/env python
#-*- coding: utf-8 -*-
import unittest
from model.sentence import *
from csv_file_reader import load_csv_test_file

class TestSubject(unittest.TestCase):

    def setUp(self):
        self.input_texts = load_csv_test_file('tests/input/subject_test.csv') 
        self.input_texts_with_msi = load_csv_test_file('tests/input/subject_with_msi_test.csv') 

    def blah_test_entities_at_verb_level(self):
        examples = [
            (u'todas las noches viene el cartero',      [u'todas las noches', u'el cartero']),
            (u'las cartas del cartero llegaron tarde',  [u'las cartas de el cartero']),
            (u'el golpeador golpeó mucho a su esposa',  [u'el golpeador']),
        ]

        for (input_text, expected_entities) in examples:
            sentence = Sentence(input_text)
            entities_at_verb_level = [e.__str__() for e in filter(lambda entity: entity.level == sentence.verb.level, sentence.entities)]
            self.assertEqual(expected_entities, entities_at_verb_level)

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

            sentence = Sentence(input_text)
            print "trying: ", sentence

            self.assertEqual(int(expected_subject_person), sentence.subject.msi['person'])
            self.assertEqual(expected_subject_number, sentence.subject.msi['number'])
            self.assertEqual(expected_subject_gender, sentence.subject.msi['gender'])
            self.assertEqual(expected_subject, sentence.subject.__str__().decode('utf-8'))

            self.assertEqual(int(expected_verb_person), sentence.verb.msi['person'])
            self.assertEqual(expected_verb_number, sentence.verb.msi['number'])
            self.assertEqual(expected_verb_gender, sentence.verb.msi['gender'])
            self.assertEqual(expected_verb, sentence.verb.lemma.__str__().decode('utf-8'))

    def blah_test_subject_active_voice(self):
        for (input_text, expected_subject) in self.input_texts:
            print input_text
            sentence = Sentence(input_text)
            self.assertEqual(expected_subject, sentence.subject.__str__().strip().decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
