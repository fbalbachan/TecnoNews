#!/usr/bin/env python
#-*- coding: utf-8 -*-
import unittest

class TestBase(unittest.TestCase):
    def tearDown(self):
        print '<parseable_output test="' + super(TestBase, self).id().split(".")[-1] + '" clase="' + self.__class__.__name__ + '">'
        print [self.failed, len(self.failed), self.passed, len(self.passed)]
        print "</parseable_output>"

    def setUp(self):
        self.passed = []
        self.failed = []

    def _print_data(self):
        print "writing to log..."

    def assertEqual(self, first, second, msg=None):
        super(TestBase, self).assertEqual(first, second, msg)
