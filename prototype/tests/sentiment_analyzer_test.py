#!/usr/bin/env python
#-*- coding: utf-8 -*-
import unittest
from model.sentence import *
from csv_file_reader import load_csv_test_file

class TestSentimentAnalyzer(unittest.TestCase):

    def setUp(self):
        self.input_texts = load_csv_test_file('tests/input/sentiment_analyzer.csv')

    def test_sentiment_analyzer(self):
        for (input_text, expected_subject_sentiment) in self.input_texts:
            sentence = Sentence(input_text)
            expected_subject_sentiment = 0.0
            print "trying: ", sentence
            self.assertEquals(expected_subject_sentiment, sentence.subject.sentiment)


if __name__ == '__main__':
    unittest.main()
