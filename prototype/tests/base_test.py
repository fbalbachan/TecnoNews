#!/usr/bin/env python
#-*- coding: utf-8 -*-
import unittest

class TestBase(unittest.TestCase):
    def tearDown(self):
        print "<parseable_output>"
        print [self.failed, len(self.failed), self.passed, len(self.passed)]
        print "</parseable_output>"

    def setUp(self):
        self.passed = []
        self.failed = []
