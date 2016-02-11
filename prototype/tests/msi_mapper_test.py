#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import unittest

from src.ling.msi_mapper import tag_to_full_msi, msi
from src.ling.gender import Gender
from src.ling.number import Number
from tests.base_test import TestBase

class TestMSIMapper(TestBase):
    
    def setUp(self):
        super(TestMSIMapper, self).setUp()

    def test_tag_to_full_msi_normal_case(self):
        normal_tag = "AQ0MS0"

        expected = {"category": u"adjective", "type": u"calificative", "grade": None,
                    "gender": Gender.masculine, "number": Number.singular, "function": None}

        expected_json = ('{"category": "adjective", "function": null, "grade": null, '
                         + '"gender": "masculine", "number": "singular", "type": "calificative"}')

        result = tag_to_full_msi(normal_tag)
        result_json = json.dumps(result)
        self.assertEqual(expected, result)
        self.assertEqual(expected_json, result_json.encode('utf-8'))

    def test_msi_normal_case(self):
        a_msi = {"category": u"adjective", "type": u"calificative", "grade": None,
                 "gender": Gender.masculine, "number": Number.singular, "function": None}

        expected = {"gender": Gender.masculine, "number": Number.singular, "person": 3}

        expected_json = '{"person": 3, "number": "singular", "gender": "masculine"}'

        result = msi(a_msi)
        result_json = json.dumps(result)
        self.assertEqual(expected, result)
        self.assertEqual(expected_json, result_json.encode('utf-8'))

    def test_tag_to_full_msi_special_case(self):
        self.special_case_tag = "NCMN000"

        expected = {'category': u'noun', 'semantic_classification': None,
                    'grade': None, 'gender': Gender.masculine, 'number': Number.invariable,
                    'type': u'common'}

        expected_json = (u'{"category": "noun", "semantic_classification": null, "grade": null, '
                         + u'"gender": "masculine", "number": "invariable", "type": "common"}').encode('utf-8')

        result = tag_to_full_msi(self.special_case_tag)
        result_json = json.dumps(result, ensure_ascii = False)
        self.assertEqual(expected, result)
        self.assertEqual(expected_json, result_json.encode('utf-8'))

    def test_msi_special_case(self):
        a_msi = {"category": u"adjective",       "type": u"calificative",       "grade": None,
                 "gender": Gender.masculine, "number": Number.singular, "function": None}

        expected = {"gender": Gender.masculine, "number": Number.singular, "person": 3}

        expected_json = '{"person": 3, "number": "singular", "gender": "masculine"}'

        result = msi(a_msi)
        result_json = json.dumps(result)
        self.assertEqual(expected, result)
        self.assertEqual(expected_json, result_json.encode('utf-8'))


if __name__ == '__main__':
    unittest.main()
