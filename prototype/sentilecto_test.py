#!/usr/bin/env python
#-*- coding: utf-8 -*-
import random, unittest
from conf import *
from estructura import *
from palabra import *
from oracion import *
from texto import *
from est import *

class TestOracion(unittest.TestCase):

    def setUp(self):
        sentence = u'el vocero que habla anuncia medidas.'
        self.o = Oracion(sentence)

    def test_quitar(self):
        gv = self.o.by_label('grup-verb')[1]
        self.assertEqual(gv.__str__(), u'el vocero que habla anuncia medidas')

        sub = self.o.by_label('subord-rel')[0]
        self.assertEqual(sub.__str__(), u'que habla')

        resultado = gv.quitar([sub])
        self.assertEqual(resultado.__str__(), u'el vocero anuncia medidas')

    def test_clausula(self):
        main_clause = self.o.clauses[0]
        self.assertEqual(main_clause.__repr__(), '''grup-verb[[u'el', u'vocero', u'anuncia', u'medidas']]''')
        self.assertTrue(main_clause.principal)

        subordinate_clause = self.o.clauses[1]
        self.assertEqual(subordinate_clause.__repr__(), '''subord-rel[[u'que', u'habla']]''')
        self.assertFalse(subordinate_clause.principal)

    def test_entidades(self):
        main_clause = self.o.clauses[0]
        main_clause.hallar_entidades()
        self.assertEqual(main_clause.entidades_sujeto[0].__str__(), u'el vocero')
        self.assertEqual(main_clause.entidades_no_sujeto[0].__str__(), u'medidas')

class TestAsignacionNominalYAsignacionPorScript(unittest.TestCase):

    def setUp(self):
        sentence1 = u'Fernando ama a María.'
        self.o1 = Oracion(sentence1)
        
        sentence2 = u'No puedo vivir sin amar.'
        self.o2 = Oracion(sentence2)

    def test_svo(self):
        main_clause1 = self.o1.clauses[0]
        main_clause2 = self.o2.clauses[0]

        fernando = main_clause1.entidades_sujeto[0]
        maria = main_clause1.entidades_no_sujeto[0]
        
        main_clause1.hallar_entidades()
        self.assertEqual(fernando.__str__(), u'Fernando')
        self.assertEqual(maria.__str__(), 'Mar\xc3\xada')

        amar = main_clause2.entidades_no_sujeto[0]

        main_clause2.hallar_entidades()
        self.assertTrue(main_clause2.sujeto_es_tacito)
        self.assertEqual(amar.__str__(), u'amar')

        # chequear valores
        # Amar (sentence id: 0) -> (60, 0)
        # una conducta normal (sentence id: 0) -> (60, 0)
        # Fernando (sentence id: 0) -> (60, 0)
        # María (sentence id: 0) -> (60, 0)
        # self.assertEqual( , )

    def test_svo(self):
        # Amar es un vicio
        # Amar 60,30
        # vicio 60,30
        pass


class TestSentiment(unittest.TestCase):

    def setUp(self):
        sentence = u'vocero que habla anuncia.'
        self.o = Oracion(sentence)

    def test_X(self):
        self.assertEqual(1, 1)


if __name__ == '__main__':
    unittest.main()
