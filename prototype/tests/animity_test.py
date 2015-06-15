#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Martín Caramés Abente'

import unittest


class TestAnimityComputation(unittest.TestCase):
    #
    # This is a stub for the test suit regarding animity calculus (to be completed)
    #

    def setUp(self):
        self.input_texts = [
            # ('', '')
        ]

    def test_check_animity(self):
        pass
        # analyzer = SentenceAnalyzer(FreelingTreeRepository("tests/input/trees"))

        # for (input_text, expected_animity) in self.input_texts:
        #   print "trying: %s .. " % input_text,

        #   sentence = Sentence(input_text)
        #   analyzer.analyze(sentence)

        #   print "OK"


if __name__ == '__main__':
    unittest.main()
