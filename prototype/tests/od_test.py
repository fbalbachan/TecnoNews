#!/usr/bin/env python
#-*- coding: utf-8 -*-
import unittest
from model.sentence import *

class TestOD(unittest.TestCase):

    def setUp(self):
        self.input_texts_with_ods = [
                (u'el cartero trae las cartas', u'las cartas'),
                (u'lo matamos a su padre', u'lo'),
                (u'estoy lidiando con mis alumnos de la facultad durante todo el mes', u'None'),
                (u'esto me parece muy bien', u'None'),
                (u'no me anduvo el auto', u'None'),
                (u'a los niños debemos educarlos con propiedad', u'los'),
                (u'puedes comprarlo para navidad', u'lo'),
                (u'ella odia correr por el parque a la noche', u'correr por el parque a la noche'),
                (u'a el hombre lo atacaron ayer por la espalda', u'lo'),
                (u'cuchillo en mano, el hombre ataca a la bestia', u'la bestia'),
                (u'tienen que dejar de fumar cigarrillos', u'None'),
                # (u'durante noches enteras fueron perseguidas a sol y sombra las mujeres', u'las mujeres'),
                (u'todos los meses llegaba el cartero con una excelente noticia', u'None'),
                (u'vos y yo somos tal para cual', u'None'),
                (u'las mujeres necesitamos comer todos los días', u'comer todos los días'),
                (u'durante toda la noche me dijo eso mi amigo',	u'mi amigo'),
                (u'la casa se encuentra sobre la colina', u'None'),
                (u'el mueble de mi abuelo se rompe con facilidad', u'None'),
                (u'odio caminar por el bosque',	u'caminar por el bosque'), 
                (u'me gusta caminar por el bosque', u'None'),
                ## (u'puede un hombre cambiar al mundo', u'cambiar a el mundo'), # FAIL expected
                (u'un hombre puede cambiar el mundo', u'el mundo'),
                (u'el perro y el gato son dos animales', u'None'),
                (u'todo lo dicho es para bien', u'None'),
                (u'los hombres pueden haber sido malos', u'None'),
                (u'lloraba mucho, las manos apretadas', u'None'),
                (u'lloraba mucho la condesa de Londres', u'None'),
                (u'La casa nunca ha sido tan codiciada antes de su venida', u'None'),
                (u'la casa, pese a las opiniones ajenas, no debe estar ubicada en la colina', u'None'),
                (u'ella puede comer de todo', u'None'),
                (u'la casa no estaba en venta', u'None'),
                (u'mi colega y yo trabajamos en conjunto para desarrollar estos algoritmos', u'None'),
                ## (u'hemos sido perseguidas días enteros por las asesinas', u'None'),
                ## (u'llueve en la ciudad sin parar', u'None'),
             ]

    def test_get_OD(self):
        for (input_text, expected_od) in self.input_texts_with_ods:
            sentence = Sentence(input_text)
            result_od = sentence.od.__str__()

            print "input: ", input_text
            print "expected: ", expected_od
            print "got: ", result_od
            print sentence.evidence
            
            self.assertTrue(sentence.is_active)
            self.assertEquals(expected_od.encode('utf-8'), sentence.od.__str__())


if __name__ == '__main__':
    unittest.main()
