#!/usr/bin/env python
#-*- coding: utf-8 -*-
import json
import unittest

from src.ling.msi_mapper import tag2fullmsi, msi


class TestMSIMapper(unittest.TestCase):

    def test_tag2fullmsi_normal_case(self):
        normal_tag = "AQ0MS0"
        expected      = {"category": u"adjective", "type": u"calificative", "grade": None, "gender": u"masculine", "number": u"singular", "function": None}
        expected_json = '{"category": "adjective", "function": null, "grade": null, "gender": "masculine", "number": "singular", "type": "calificative"}'
        result = tag2fullmsi(normal_tag)
        result_json = json.dumps(result)
        self.assertEqual(expected, result)
        self.assertEqual(expected_json, result_json.encode('utf-8'))

    def test_msi_normal_case(self):
        a_msi = {"category": u"adjective", "type": u"calificative", "grade": None, "gender": u"masculine", "number": u"singular", "function": None}
        expected      = {"gender": u"masculine", "number": u"singular", "person": 3}
        expected_json = '{"person": 3, "number": "singular", "gender": "masculine"}'
        result = msi(a_msi)
        result_json = json.dumps(result)
        self.assertEqual(expected, result)
        self.assertEqual(expected_json, result_json.encode('utf-8'))

    def test_tag2fullmsi_special_case(self):
        self.special_case_tag = "NCMN000"
        expected      = {"category": u"noun", "type": u"common", "gender": u"masculine", "number": u"invariable", "semantic_classification": None, "grade": None}
        expected      = {'category': u'noun', 'semantic_classification': None, 'grade': None, 'gender': u'masculine', 'number': u'invariable', 'type': u'common'}
        expected_json = u'{"category": "noun", "semantic_classification": null, "grade": null, "gender": "masculine", "number": "invariable", "type": "common"}'.encode('utf-8')
        result = tag2fullmsi(self.special_case_tag)
        result_json = json.dumps(result, ensure_ascii = False)
        self.assertEqual(expected, result)
        self.assertEqual(expected_json, result_json.encode('utf-8'))

    def test_msi_special_case(self):
        a_msi = {"category": u"adjective", "type": u"calificative", "grade": None, "gender": u"masculine", "number": u"singular", "function": None}
        expected      = {"gender": u"masculine", "number": u"singular", "person": 3}
        expected_json = '{"person": 3, "number": "singular", "gender": "masculine"}'
        result = msi(a_msi)
        result_json = json.dumps(result)
        self.assertEqual(expected, result)
        self.assertEqual(expected_json, result_json.encode('utf-8'))


if __name__ == '__main__':
    unittest.main()
