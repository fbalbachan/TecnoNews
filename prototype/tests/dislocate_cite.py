#!/usr/bin/env python
#-*- coding: utf-8 -*-
import unittest

from src.ling.freelingDictionaryParser import FreelingDictionaryParser
from src.model.paragraph.paragraph import Paragraph
from src.model.paragraph.paragraphAnalyzer import ParagraphAnalyzer
from src.model.sentence.sentenceAnalyzer import SentenceAnalyzer
from src.rewrite.rewriter import Rewriter
from src.rewrite.strategy.textualCite import TextualCite
from tests.freelingTreeRepository import FreelingTreeRepository


class TestRewriter(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        print "[Rewriter test]"

        self.sentenceAnalyzer = SentenceAnalyzer(FreelingTreeRepository("tests/input/trees"))
        self.analyzer = ParagraphAnalyzer(self.sentenceAnalyzer)

    def __(self):
        print "___________----____--_"
        ontology = FreelingDictionaryParser.from_resource()
        print ontology.get_lexical_form("haber", { "mode" : "indicative", "time" : "presente", "person" : 2, "number" : "singular"})

    def test_dislocate_cite(self):
        self.strategies = [TextualCite([True], [""])]

        # FIXME: kase when the Fc next to '"' clousing simbol is inside of another structure
        # self.kase('"Desafortunadamente, son muchos", dijo el hombre y añadió: "Nuestros heridos están graves".', '"--Desafortunadamente, son muchos", dijo el hombre y añadió: "Nuestros heridos están graves".')

        # TODO: Write Correct result case
        # Maradona dijo esto: " "
        # self.kase('“Yo sabía que las mejores notas no definen a los estudiantes que han desarrollado un aprendizaje más profundo”, dijo al informar de la génesis de su última obra, así como tampoco “los que ganan más dinero”.',
        #           '“Yo sabía que las mejores notas no definen a los estudiantes que han desarrollado un aprendizaje más profundo”, dijo al informar de la génesis de su última obra, así como tampoco “los que ganan más dinero”.')
        self.kase('“El segundo es asegurar que no sufran de enfermedades transmisibles que no les permitan desempeñar al máximo las tareas de un policía entrenado”, afirmó.',
                  'afirmó, “El segundo es asegurar que no sufran de enfermedades transmisibles que no les permitan desempeñar al máximo las tareas de un policía entrenado”.')
        self.kase('"Desafortunadamente ganamos", dijo el hombre, "Nuestros heridos están graves"', 'el hombre, "Nuestros heridos están graves" dijo, "Desafortunadamente ganamos"')
        self.kase('“Una cosa es lo que afirmen los periódicos y otra la realidad de las cosas”, comentó Lobón, que reveló que Hacienda y el Atlético están en este momento negociando modificaciones en el convenio patrimonial de 2008 para “quitar todo aquello que estaba afectado por los juegos olímpicos y para programar la nueva situación y la ejecución de obras”.',
                  'Lobón, que reveló que Hacienda y el Atlético están en este momento negociando modificaciones en el convenio patrimonial de 2008 para “quitar todo aquello que estaba afectado por los juegos olímpicos y para programar la nueva situación y la ejecución de obras” comentó, “Una cosa es lo que afirmen los periódicos y otra la realidad de las cosas”.')
        self.kase('“Es un paso adelante clave para hacer de Nueva York una ciudad más igual, abierta y conectada”, asegura el alcalde demócrata.',
                  'el alcalde demócrata asegura, “Es un paso adelante clave para hacer de Nueva York una ciudad más igual, abierta y conectada”.')
        self.kase('“Se suspende esta negociación hasta tanto no se aclare y se liberen estas personas”, dijo Maradona hoy, rodeado de la cúpula militar.',
                  'Maradona hoy, rodeado de la cúpula militar dijo, “Se suspende esta negociación hasta tanto no se aclare y se liberen estas personas”.')
        self.kase('“Se suspende esta negociación hasta tanto no se aclare y se liberen estas personas”, dijo hoy, rodeado de la cúpula militar.',
                  'hoy, rodeado de la cúpula militar dijo, “Se suspende esta negociación hasta tanto no se aclare y se liberen estas personas”.')
        self.kase('Con soltura Maradona dijo, "no fue con la mano".', '"no fue con la mano", dijo Con soltura Maradona.')
        self.kase('"fue con la mano", dijo Maradona con soltura.', 'Maradona con soltura dijo, "fue con la mano".')
        self.kase('Maradona dijo, "no fue con la mano".', '"no fue con la mano", dijo Maradona.')
        self.kase('Maradona dijo: "no fue con la mano".', '"no fue con la mano", dijo Maradona.')
        self.kase('Diego Maradona comenta: "no fue con la mano".', '"no fue con la mano", comenta Diego Maradona.')

        # TODO:
        self.kase('El mejor jugador de todos los tiempos dijo: "no fue con la mano".',
                  '"no fue con la mano", dijo El mejor jugador de todos los tiempos.')

        self.kase('Ellos comentaron: "vivos se los llevaron, vivos los queremos".',
                   '"vivos se los llevaron, vivos los queremos", comentaron Ellos.')

        #TODO: case with distance 3
        # avoid false positives
        self.kase('Entretanto, el gobierno federal anunció que presentará una "Comisión de Estado" que dictará los lineamientos para enfrentar la inseguridad en el país.',
                  'Entretanto, el gobierno federal anunció que presentará una "Comisión de Estado" que dictará los lineamientos para enfrentar la inseguridad en el país.')

        #Fixme: case long cite
        # self.kase('“Es bastante extraordinario que podamos hacer esto; rastrear un cometa y mirar la evolución de un cometa. Tenemos un asiento en primera fila”, afirmó el ingeniero de sistemas de aterrizaje de la ESA',
        #           'Afirmó el ingeniero de sistemas de aterrizaje de la ESA: “Es bastante extraordinario que podamos hacer esto; rastrear un cometa y mirar la evolución de un cometa. Tenemos un asiento en primera fila”')


    def kase(self, source, edited):
        print "Case:", source
        analyzer = self.analyzer

        paragraph = Paragraph.from_text(source)
        analyzer.analyze(paragraph)

        text = Rewriter(paragraph, self.ontology, self.strategies).rewrite()
        print "\t[SOURCE]", paragraph.text
        print "\t[EDITED]", text

        # if not text == edited:
        #     import difflib
        #     diff = difflib.ndiff(None, text, edited)
        #

        self.assertEqual(text, edited)

    ontology = Rewriter.ontology

if __name__ == '__main__':
    # unittest.main()
    suite = unittest.TestSuite()

    suite.addTest(unittest.makeSuite(TestRewriter))

    unittest.TextTestRunner(verbosity=2).run(suite)
