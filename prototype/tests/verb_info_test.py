#!/usr/bin/env python
#-*- coding: utf-8 -*-
import unittest
from ling.verb_info import *

class TestVerbInfo(unittest.TestCase):

    def test_verb_scripts_and_boxes(self):
        examples = [
            (u'charlatanear',
             'AGENTIVE',
             'INTRANSITIVE',
             {'regimen': False, 'oi': True, 'od': False, 'verb': True, 'equative': False, 'adjuncts': True, 'subject': True}),
        ]

        for (input_verb, expected_script, expected_transitivity, expected_boxes) in examples:
            print "trying: ", input_verb
            self.assertEqual(expected_script, get_script_class(input_verb))
            self.assertEqual(expected_transitivity, get_transitivity(input_verb))
            self.assertEqual(expected_boxes, allowed_boxes(get_transitivity(input_verb)))

if __name__ == '__main__':
    unittest.main()
