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
        ontology = FreelingDictionaryParser.from_resource()
        print ontology.get_lexical_form("haber", { "mode" : "indicative", "time" : "presente", "person" : 2, "number" : "singular"})

    def test_dislocate_cite(self):
        self.strategies = [TextualCite([True], [""])]

        # TODO:
        # Case fist level parsing SN SN Verb F-no-c F-no-c(") Something F-no-c F-term
        # self.kase('El mejor jugador de todos los tiempos, Diego Armando Maradona, declaró: "no fue con la mano".', '"no fue con la mano", declaró el mejor jugador de todos los tiempos, Diego Armando Maradona.')

        self.kase('Maradona dijo, "no fue con la mano".', '"no fue con la mano", dijo Maradona.')
        self.kase('Maradona dijo: "no fue con la mano".', '"no fue con la mano", dijo Maradona.')
        self.kase('Diego Maradona comenta: "no fue con la mano".', '"no fue con la mano", comenta Diego Maradona.')

        self.kase('El mejor jugador de todos los tiempos dijo: "no fue con la mano".',
                  '"no fue con la mano", dijo el mejor jugador de todos los tiempos.')

        self.kase('Ellos comentaron: "vivos se los llevaron, vivos los queremos".',
                   '"vivos se los llevaron, vivos los queremos", comentaron ellos.')

        #TODO: case with distance 3
        # self.kase('Fernando dijo lo siguiente, "esto debe funcionar"., "")
        # self.kase('Diego Maradona afirmó: "No fue con la mano. El gol fue válido".',
        #           '"No fue con la mano. El gol fue válido", afirmó Diego Maradona.')

        # self.kase('Escribieron el mensaje: "vivos se los llevaron, vivos los queremos".',
        #            '"vivos se los llevaron, vivos los queremos", escribieron el mensaje.')

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

        self.assertEqual(text, edited)

    ontology = Rewriter.ontology

if __name__ == '__main__':
    # unittest.main()
    suite = unittest.TestSuite()

    suite.addTest(unittest.makeSuite(TestRewriter))

    unittest.TextTestRunner(verbosity=2).run(suite)
