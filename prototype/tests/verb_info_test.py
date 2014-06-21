#!/usr/bin/env python
#-*- coding: utf-8 -*-
import unittest

from src.ling.verb_info import get_script_class, get_transitivity, allowed_boxes


class TestVerbInfo(unittest.TestCase):

    def test_verb_scripts_and_boxes(self):
        examples = [
            (u'charlatanear',
             'AGENTIVE',
             'INTRANSITIVE',
             [ 'verb', 'subject', 'oi', 'instrument_goal', 'adjuncts' ]),
        ]

        for (input_verb, expected_script, expected_transitivity, expected_boxes) in examples:
            print "trying: ", input_verb
            self.assertEqual(expected_script, get_script_class(input_verb))
            self.assertEqual(expected_transitivity, get_transitivity(input_verb))
            self.assertEqual(expected_boxes, allowed_boxes(get_transitivity(input_verb)))

if __name__ == '__main__':
    unittest.main()
