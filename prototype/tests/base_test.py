#!/usr/bin/env python
#-*- coding: utf-8 -*-
import unittest

class TestBase(unittest.TestCase):
    def tearDown(self):
        print '<parseable_output test="' + self._get_current_test_name() + '" clase="' + self.__class__.__name__ + '">'
        print [self.failed, len(self.failed), self.passed, len(self.passed)]
        print "</parseable_output>"

    def setUp(self):
        self.passed = []
        self.failed = []
        self.input  = ""

    def _get_current_test_name(self):
        return super(TestBase, self).id().split(".")[-1]
    
    def assertEqual(self, first, second, msg=None):
        try :
            super(TestBase, self).assertEqual(first, second, msg)
            self.passed.append({"method" : self._get_current_test_name(), "expected" : first , "found" : second, "input" : self.input})
        except Exception, e:
            self.failed.append({"message" : str(e), "method" : self._get_current_test_name(), "expected" : first,"found":second , "input" : self.input })
