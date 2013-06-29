#!/usr/bin/env python
#-*- coding: utf-8 -*-
import unittest
from model.sentence import *

class TestContainedEntities(unittest.TestCase):

    def setUp(self):

        self.data = [
            (u'el hombre de la esquina rosada llega',     u'el hombre de la esquina rosada',    u'la esquina rosada'),
            (u'las doradas manzanas del sol brillan',     u'las doradas manzanas de el sol',    u'el sol'),
            (u'la selva de los animales existe',          u'la selva de los animales',          u'los animales'),
            (u'los animales de la selva comen',           u'los animales de la selva',          u'la selva'),
        ]

    def test_get_only_container_entity(self):
        for (input_text, expected_container_entity, expected_removed_entity) in self.data:
            entities = [e.__str__() for e in Sentence(input_text).get_entities()]
            print "expected container entity: %s | expected removed entity: %s" % (expected_container_entity, expected_removed_entity)
            print "entities", entities
            self.assertTrue(expected_container_entity in entities)
            self.assertTrue(expected_removed_entity not in entities)


if __name__ == '__main__':
    unittest.main()
