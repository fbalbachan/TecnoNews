#!/usr/bin/env python
#-*- coding: utf-8 -*-
import unittest
from model.sentence import *

class TestSubject(unittest.TestCase):

    def test_entities_at_verb_level(self):
        examples = [
            (u'todas las noches viene el cartero',      [u'todas las noches', u'el cartero']),
            (u'las cartas del cartero llegaron tarde',  [u'las cartas de el cartero']),
            (u'el golpeador golpeó mucho a su esposa',  [u'el golpeador']),
        ]

        for (input_text, expected_entities) in examples:
            sentence = Sentence(input_text)
            entities_at_verb_level = [e.__str__() for e in filter(lambda entity: entity.level == sentence.verb.level, sentence.entities)]
            self.assertEqual(expected_entities, entities_at_verb_level)

    def test_subject(self):
        examples = [
            (u'todas las noches viene el cartero',
             {'person': 3, 'number': u'singular', 'gender': u'neutral'},
             u'el cartero',
             {'person': 3, 'number': u'singular', 'gender': u'neutral'},
             u'venir'),

            (u'golpeó mucho a su esposa',
             {'person': 3, 'number': u'singular', 'gender': u'neutral'},
             u'él',
             {'person': 3, 'number': u'singular', 'gender': u'neutral'},
             u'golpear'),

            (u'me gustó caminar por el bosque',
             {'person': 3, 'number': u'singular', 'gender': u'neutral'},
             u'caminar por el bosque',
             {'person': 3, 'number': u'singular', 'gender': u'neutral'},
             u'gustar',
            ),

            (u'llovió toda la noche',
             {'person': 0, 'number': u'singular', 'gender': u'neutral'},
             'None',
             {'person': 0, 'number': u'singular', 'gender': u'neutral'},
             u'llover'),

            (u'vos y yo comemos pizza',
             {'person': 1, 'number': u'plural', 'gender': u'neutral'},
             u'vos y yo',
             {'person': 1, 'number': u'plural', 'gender': u'neutral'},
             u'comer'),
        ]

        for (input_text,
             expected_subject_msi,
             expected_subject,
             expected_verb_msi,
             expected_verb) in examples:

            sentence = Sentence(input_text)

            subject = sentence.subject
            self.assertEqual(expected_subject, subject.__str__().decode('utf-8'))

            verb_msi = sentence.verb.msi
            print sentence.verb, sentence.verb.msi
            self.assertEqual(expected_verb_msi, verb_msi)

    def test_subject_active_voice(self):
        examples = [
            { 'input_text' : u'matamos a su padre',
              'subject' : u'nosotros', # {[FIRST] [PLURAL]}
              'verb' : u'matar', # {[FIRST] [PLURAL]}
          },

            { 'input_text' : u'estoy lidiando con mis alumnos de la facultad durante todo el mes',
              'subject' : u'yo', # {[FIRST] [SINGULAR]}
              'verb' : u'lidiar', # {[FIRST] [SINGULAR]}
          },
            
            { 'input_text' : u'esto me parece muy bien',
              'subject' : u'esto', # {[SINGULAR]}
              'verb' : u'parecer', # {[THIRD] [SINGULAR]}
          },

            { 'input_text' : u'llueve en la ciudad sin parar',
              'subject' : 'None',
              'verb' : u'llover', # {[THIRD] [SINGULAR]}
          },

            { 'input_text' : u'ella odia correr por el parque a la noche',
              'subject' : u'ella', # {[THIRD] [SINGULAR] [FEMALE]}
              'verb' : u'odiar', # {[THIRD] [SINGULAR]}
          },

            { 'input_text' : u'lo matamos a su padre',
              'subject' : u'nosotros', # {[FIRST] [PLURAL]}
              'verb' : u'matar', # {[FIRST] [PLURAL]}
          },
  
            { 'input_text' : u'no me anduvo el auto',
              'subject' : u'el auto', # {[SINGULAR] [MALE]}
              'verb' : u'andar', # {[THIRD] [SINGULAR]}
          },

            { 'input_text' : u'a los niños debemos educarlos con propiedad',
              'subject' : u'nosotros', # {[FIRST] [PLURAL]}
              'verb' : u'educar', # {[FIRST] [PLURAL]}
          },

            { 'input_text' : u'puedes comprarlo para navidad',
              'subject' : u'tú', # {[SECOND] [SINGULAR]}
              'verb' : u'comprar', # {[SECOND] [SINGULAR]}
          },

            { 'input_text' : u'a el hombre lo atacaron ayer por la espalda',
              'subject' : u'ellos', # {[THIRD] [PLURAL]}
              'verb' : u'atacar', # {[THIRD] [PLURAL]}
          },

            { 'input_text' : u'todos los meses llegaba el cartero con una excelente noticia',
              'subject' : u'el cartero', # {[SINGULAR] [MALE]}
              'verb' : u'llegar', # {[THIRD] [SINGULAR]}
          },

            { 'input_text' : u'vos y yo somos tal para cual',
              'subject' : u'vos y yo', # {[FIRST] [PLURAL]}
              'verb' : u'ser', # {[FIRST] [PLURAL]}
          },

            { 'input_text' : u'odio caminar por el bosque',
              'subject' : u'yo', # {[FIRST] [SINGULAR]}
              'verb' : u'odiar', # {[FIRST] [SINGULAR]}
          },

            { 'input_text' : u'me gusta caminar por el bosque',
              'subject' : u'caminar por el bosque', # {[SINGULAR]}
              'verb' : u'gustar', # {[THIRD] [SINGULAR]}
          },

            { 'input_text' : u'puede un hombre cambiar al mundo',
              'subject' : u'un hombre', # {[SINGULAR] [MALE]}
              'verb' : u'poder', # {[THIRD] [SINGULAR]}
          },

            { 'input_text' : u'los hombres pueden haber sido malos',
              'subject' : u'los hombres', # {[PLURAL] [MALE]}
              'verb' : u'haber', # {[THIRD] [PLURAL]}
          },

            { 'input_text' : u'Ella puede comer de todo',
              'subject' : u'Ella', # {[THIRD] [SINGULAR] [FEMALE]}
              'verb' : u'comer', # {[THIRD] [SINGULAR]}
          },

            { 'input_text' : u'lloraba mucho la condesa de Londres',
              'subject' : u'la condesa de Londres', # {[SINGULAR] [FEMALE]}
              'verb' : u'llorar', # {[THIRD] [SINGULAR]}
          },
   
          { 'input_text' : u'la casa, pese a las opiniones ajenas, no debe estar ubicada en la colina',
            'subject' : u'la casa', #{[SINGULAR] [FEMALE]}
            'verb' : u'estar', # {[THIRD] [SINGULAR]}
          },

            { 'input_text' : u'lloraba mucho, las manos apretadas',
              'subject' : u'él', # {[THIRD] [SINGULAR]}
              'verb' : u'llorar', # {[THIRD] [SINGULAR]}
          },

            { 'input_text' : u'cuchillo en mano, el hombre ataca a la bestia',
              'subject' : u'el hombre', # {[SINGULAR] [MALE]}
              'verb' : u'atacar', # {[THIRD] [SINGULAR]}
          },

            { 'input_text' : u'el perro y el gato son dos animales',
              'subject' : u'el perro y el gato', # {[PLURAL] [MALE]}
              'verb' : u'ser', # {[THIRD] [PLURAL]}
          },

            { 'input_text' : u'todo lo dicho es para bien',
              'subject' : u'lo dicho', # {[SINGULAR]}
              'verb' : u'ser', # {[THIRD] [SINGULAR]}
          },
            
            { 'input_text' : u'el mueble de mi abuelo se rompe con facilidad',
              'subject' : u'el mueble de mi abuelo', # {[SINGULAR] [MALE]}
              'verb' : u'romper', # {[THIRD] [SINGULAR]}
          },

            { 'input_text' : u'la casa se encuentra sobre la colina',
              'subject' : u'la casa', # {[SINGULAR] [FEMALE]}
              'verb' : u'encontrar', # {[THIRD] [SINGULAR]}
          },
            
          #   { 'input_text' : u'las mujeres necesitamos comer todos los días',
          #     'subject' : ???, # {[SINGULAR]}
          #     'verb' : u'decir', # {[THIRD] [SINGULAR]}
          # },

      ]
      
        for example in examples:
            input_text, expected_subject, expected_verb = example['input_text'], example['subject'], example['verb']
            print input_text, ' - ', expected_subject, ' - ', expected_verb

            sentence = Sentence(input_text)

            subject = sentence.subject
            self.assertEqual(expected_subject, subject.__str__().decode('utf-8'))
            
            verb = sentence.verb
            self.assertEqual(expected_verb, verb.lemma)

       
    def test_subject_passive_voice(self):
        examples = [

          #   { 'input_text' : u'durante noches enteras fueron perseguidas a sol y sombra las mujeres',
          #     'subject' : u'las mujeres',
          #     'verb' : u'perseguir', # {[THIRD] [PLURAL] [FEMALE]}
          # },

          #   { 'input_text' : u'hemos sido perseguidas días enteros por las asesinas',
          #     'subject' : u'nosotras', # {[PLURAL] [FEMALE]}
          #     'verb' : u'perseguir', # {[FIRST] [PLURAL] [FEMALE]}
          # },

          #   { 'input_text' : u'fue manipulada mucho, cuchillo en mano, la condesa de Londres',
          #     'subject' : u'la casa', # {[SINGULAR] [FEMALE]}
          #     'verb' : u'ser', # {[THIRD] [SINGULAR]}
          # },

      ]
      
        for example in examples:
            input_text, expected_subject, expected_verb = example['input_text'], example['subject'], example['verb']
            print input_text, ' - ', expected_subject, ' - ', expected_verb

            sentence = Sentence(input_text)

            subject = sentence.subject
            self.assertEqual(expected_subject, subject.__str__())
            
            verb = sentence.verb
            self.assertEqual(expected_verb, verb.lemma)


if __name__ == '__main__':
    unittest.main()
