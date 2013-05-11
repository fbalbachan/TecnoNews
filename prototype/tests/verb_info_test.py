#!/usr/bin/env python
#-*- coding: utf-8 -*-
import unittest
from ling.verb_info import *

class TestVerbInfo(unittest.TestCase):

    def test_verb_scripts_and_boxes(self):
        examples = [
            (u'charlatanear', 'AGENTIVE', 'INTRANSITIVE', {'od': False,
                                                           'oi': True,
                                                           'regimen': False,
                                                           'equative': False}),
        ]

        for (input_verb, expected_script, expected_transitivity, expected_boxes) in examples:
            info = verb_info(input_verb)
            self.assertEqual(expected_script,       info['script'])
            self.assertEqual(expected_transitivity, info['transitivity'])
            self.assertEqual(expected_boxes,        info['boxes'])

if __name__ == '__main__':
    unittest.main()
