#!/usr/bin/env python
#-*- coding: utf-8 -*-
import unittest
import json

class TestBase(unittest.TestCase):
    def tearDown(self):
        print '<test_output test="' + self._get_current_test_name() + '" clase="' + self.__class__.__name__ + '">'
        print "    <fails>"
        for f in self.failed :
            print "        <fail>" + json.dumps(f) + "</fail>"
        print "    </fails>"
        print "    <passes>"
        for p in self.passed :
            print "        <pass>" + json.dumps(p) + "</pass>"
        print "    </passes>"
        #print self.failed, len(self.failed), self.passed, len(self.passed)]).decode("utf-8") 
        print "</test_output>"

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

    def assertGreaterEqual(self, first, second, msg=None) : 
        try :
            super(TestBase, self).assertGreaterEqual(first, second, msg)
            self.passed.append({"method" : self._get_current_test_name(), "expected" : first , "found" : second, "input" : self.input})
        except Exception, e:
            self.failed.append({"message" : str(e), "method" : self._get_current_test_name(), "expected" : first,"found":second , "input" : self.input })


    def assertIsNotNone(self, first, second, msg=None) : 
        try :
            super(TestBase, self).assertIsNotNone(first, second, msg)
            self.passed.append({"method" : self._get_current_test_name(), "expected" : first , "found" : second, "input" : self.input})
        except Exception, e:
            self.failed.append({"message" : str(e), "method" : self._get_current_test_name(), "expected" : first,"found":second , "input" : self.input })


    def assertTrue(self, first, msg=None) : 
        try :
            super(TestBase, self).assertTrue(first, msg)
            self.passed.append({"method" : self._get_current_test_name(), "found" : first, "input" : self.input})
        except Exception, e:
            self.failed.append({"message" : str(e), "method" : self._get_current_test_name(), "found" : first, "input" : self.input })


    def assertRaises(self, first, second, msg=None) : 
        try :
            super(TestBase, self).assertRaises(first, second, msg)
            self.passed.append({"method" : self._get_current_test_name(), "expected" : first , "found" : second, "input" : self.input})
        except Exception, e:
            self.failed.append({"message" : str(e), "method" : self._get_current_test_name(), "expected" : first,"found":second , "input" : self.input })


    def assertIn(self, first, second, msg=None) : 
        try :
            super(TestBase, self).assertIn(first, second, msg)
            self.passed.append({"method" : self._get_current_test_name(), "expected" : first , "found" : second, "input" : self.input})
        except Exception, e:
            self.failed.append({"message" : str(e), "method" : self._get_current_test_name(), "expected" : first,"found":second , "input" : self.input })
