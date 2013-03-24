#!/usr/bin/env python
#-*- coding: utf-8 -*-
import unittest
from ling.msi_mapper import *

class TestMSIMapper(unittest.TestCase):

    def test_tag2msi_normal_case(self):
        normal_tag = "AQ0MS0"
        expected      = {"category": u"adjetivo", "type": u"calificativo", "grade": None, "gender": u"masculino", "number": u"singular", "function": None}
        expected_json = '{"category": "adjetivo", "function": null, "grade": null, "gender": "masculino", "number": "singular", "type": "calificativo"}'
        result = tag2msi(normal_tag)
        result_json = json.dumps(result)
        self.assertEqual(expected, result) 
        self.assertEqual(expected_json, result_json.encode('utf-8'))

    def test_filtered_msi_normal_case(self):
        msi = {"category": u"adjetivo", "type": u"calificativo", "grade": None, "gender": u"masculino", "number": u"singular", "function": None}
        expected      = {"gender": u"masculino", "number": u"singular", "person": 3}
        expected_json = '{"person": 3, "number": "singular", "gender": "masculino"}'
        result = filtered_msi(msi)
        result_json = json.dumps(result)
        self.assertEqual(expected, result) 
        self.assertEqual(expected_json, result_json.encode('utf-8'))

    # def test_tag2msi_special_case(self):
    #     self.special_case_tag = "NCMN000"
    #     expected      = {"category": u"nombre", "type": u"común", "gender": u"masculino", "number": u"invariable", "semantic_classification": u"organización", "grade": None, "person": 3}
    #     expected_json = u'{"category": "nombre", "semantic_classification": "organización", "grade": null, "gender": "masculino", "number": "invariable", "person": 3, "type": "comúan"}'.encode('utf-8')
    #     result = tag2msi(self.special_case_tag)
    #     result_json = json.dumps(result, ensure_ascii = False)
    #     self.assertEqual(expected, result) 
    #     self.assertEqual(expected_json, result_json.encode('utf-8'))


if __name__ == '__main__':
    unittest.main()
