#!/usr/bin/env python
#-*- coding: utf-8 -*-
import unittest
from model.sentence import *

class TestOI(unittest.TestCase):

    def setUp(self):
        self.input_texts_with_ois = [
                (u'el cartero trae las cartas', u''),
                (u'lo matamos a su padre', u''),
                (u'estoy lidiando con mis alumnos de la facultad durante todo el mes', u''),
                (u'esto me parece muy bien', u''),
                (u'no me anduvo el auto', u''),
                (u'a los niños debemos educarlos con propiedad', u''),
                (u'puedes comprarlo para navidad', u''),
                (u'ella odia correr por el parque a la noche', u''),
                (u'a el hombre lo atacaron ayer por la espalda', u''),
                (u'cuchillo en mano, el hombre ataca a la bestia', u''),
                (u'tienen que dejar de fumar cigarrillos', u'None'),
                # (u'durante noches enteras fueron perseguidas a sol y sombra las mujeres', u''),
                (u'todos los meses llegaba el cartero con una excelente noticia', u''),
                (u'vos y yo somos tal para cual', u''),
                (u'las mujeres necesitamos comer todos los días', u''),
                (u'durante toda la noche me dijo eso mi amigo',	u''),
                (u'la casa se encuentra sobre la colina', u''),
                (u'el mueble de mi abuelo se rompe con facilidad', u''),
                (u'odio caminar por el bosque',	u''), 
                (u'me gusta caminar por el bosque', u''),
                ## (u'puede un hombre cambiar al mundo', u''),
                (u'un hombre puede cambiar el mundo', u''),
                (u'el perro y el gato son dos animales', u''),
                (u'todo lo dicho es para bien', u''),
                (u'los hombres pueden haber sido malos', u''),
                (u'lloraba mucho, las manos apretadas', u''),
                (u'lloraba mucho la condesa de Londres', u''),
                (u'La casa nunca ha sido tan codiciada antes de su venida', u''),
                (u'la casa, pese a las opiniones ajenas, no debe estar ubicada en la colina', u''),
                (u'ella puede comer de todo', u''),
                (u'la casa no estaba en venta', u''),
                (u'mi colega y yo trabajamos en conjunto para desarrollar estos algoritmos', u''),
                ## (u'hemos sido perseguidas días enteros por las asesinas', u''),
                ## (u'llueve en la ciudad sin parar', u''),
             ]

    def test_get_OI(self):
        for (input_text, expected_oi) in self.input_texts_with_ois:
            sentence = Sentence(input_text)
            result_od = sentence.oi.__str__()

            print "input: ", input_text
            print "expected: ", expected_oi
            print "got: ", result_oi
            print sentence.evidence
            
            self.assertTrue(sentence.is_active)
            self.assertEquals(expected_oi.encode('utf-8'), sentence.oi.__str__())


if __name__ == '__main__':
    unittest.main()
