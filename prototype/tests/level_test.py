#!/usr/bin/env python
#-*- coding: utf-8 -*-
import unittest
from model.sentence import *

class TestStructureLevel(unittest.TestCase):

    def test_structure_level(self):
        sentence = Sentence(u'el hombre pasea')

        expected = set(["j-ms (3,5) el [3]",
                        "n-ms (8,10) hombre [3]",
                        "verb (13,15) pasea [1]"])
        result   = set([leaf.__repr__() for leaf in sentence.leaves])

        self.assertEqual(expected, result)

                
if __name__ == '__main__':
    unittest.main()
