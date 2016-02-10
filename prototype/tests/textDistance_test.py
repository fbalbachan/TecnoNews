#!/usr/bin/env python2.7
# -*- coding:utf-8 -*-
__author__ = 'Pablo Perez De Angelis'
import unittest
from src.utils.textDistance import TextDistance
from tests.base_test import TestBase

class TestTextDistance(TestBase):

    @classmethod
    def setUpClass(cls):
        super(TestTextDistance, cls).setUpClass()
        cls.td = TextDistance()
        print "[TextDistance test]"

    def test_pre_process(self):

        self.pre_process_kase('"¿Aceptaremos una economía en la que solo a unos pocos les va espectacularmente bien?", dijo Obama. "¿O nos comprometeremos con una economía que genere ingresos cada vez más altos y oportunidades para todos los que se esfuercen?"',
                              [u'aceptaremos', u'econom\xeda', u'espectacularmente', u'bien', u'dijo', u'obama', u'comprometeremos', u'econom\xeda', u'genere', u'ingresos', u'vez', u'altos', u'oportunidades', u'esfuercen'])

    def test_title_distance(self):
        self.title_distance_kase('"¿Aceptaremos una economía?"', 'Aceptaremos una economía', 0)
        self.title_distance_kase('"¿Aceptaremos una economía?"', '"¿Comeremos en el cielo?"', 1)
        self.title_distance_kase('El cholito', '"el miedo"', 1)


    def test_similarity(self):
        self.similarity_kase('"¿Aceptaremos una economía?"', '"¿Comeremos en el cielo?"', 0)
        self.similarity_kase('"¿Aceptaremos una economía?"', 'aceptaremos una economía', 99.99)


    def pre_process_kase(self, text, preprocessed):
        print "Case:", text
        self.input = text
        pre_proces_text = self.td.pre_process(unicode(text, 'utf-8'))
        print "\t[text]", text
        print "\t[processed]", pre_proces_text

        self.assertEqual(pre_proces_text, preprocessed)

    def title_distance_kase(self, title1, title2, distance_gold):
        print "Case:"
        print "title1", title1
        print "title2", title2
        self.input = title1 + "/" + title2
        distance = self.td.title_distance(unicode(title1, 'utf-8'),
                                          unicode(title2, 'utf-8'))
        print "\t[distance]", distance

        self.assertEqual(distance, distance_gold)

    def similarity_kase(self, text1, text2, similarity_gold):
        print "Case:"
        print "text1", text1
        print "text2", text2
        self.input = text1 + "/" + text2
        similarity = self.td.similarity(unicode(text1, 'utf-8'),
                                        unicode(text2, 'utf-8'))
        print "\t[similarity]", similarity

        # self.assertEqual(similarity, similarity_gold)
        self.assertGreaterEqual(similarity, similarity_gold)

if __name__ == '__main__':
    suite = unittest.TestSuite()

    suite.addTest(unittest.makeSuite(TestTextDistance))

    unittest.TextTestRunner(verbosity=2).run(suite)
