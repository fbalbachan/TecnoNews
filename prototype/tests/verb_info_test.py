#!/usr/bin/env python
#-*- coding: utf-8 -*-
import unittest

from src.ling.verb_info import get_sentimental_script_of, get_transitivity, allowed_boxes
from tests.base_test import TestBase

class TestVerbInfo(TestBase):

    def setUp(self):
        super(TestVerbInfo, self).setUp()

    def test_verb_scripts_and_boxes(self):
        examples = [
            ('charlatanear',
             'AGENTIVE',
             'INTRANSITIVE',
             [ 'verb', 'subject', 'oi', 'instrument_goal', 'adjuncts' ]),
        ]

        for (input_verb, expected_script, expected_transitivity, expected_boxes) in examples:
            print("trying: ", input_verb)
            self.input = input_verb
            self.assertEqual(expected_script, get_sentimental_script_of(input_verb).klass)
            self.assertEqual(expected_transitivity, get_transitivity(input_verb))
            self.assertEqual(expected_boxes, allowed_boxes(get_transitivity(input_verb)))

if __name__ == '__main__':
    unittest.main()
