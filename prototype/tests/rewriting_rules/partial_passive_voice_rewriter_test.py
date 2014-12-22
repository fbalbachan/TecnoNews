#!/usr/bin/env python
#-*- coding: utf-8 -*-
import unittest

from src.ling.freelingDictionaryParser import FreelingDictionaryParser
from src.model.paragraph.paragraph import Paragraph
from src.model.paragraph.paragraphAnalyzer import ParagraphAnalyzer
from src.model.sentence.sentenceAnalyzer import SentenceAnalyzer
from src.rewrite.rewriter import Rewriter
from src.rewrite.strategy.partialVoicePassiveStrategy import PartialVoicePassiveStrategy
from tests.freelingTreeRepository import FreelingTreeRepository


class TestRewriter(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        print "[Rewriter test]"

        self.sentenceAnalyzer = SentenceAnalyzer(FreelingTreeRepository("tests/input/trees"))
        self.analyzer = ParagraphAnalyzer(self.sentenceAnalyzer)

    def __(self):
        self.ontology = FreelingDictionaryParser.from_resource()

    def test_dislocate_cite(self):
        self.strategies = [PartialVoicePassiveStrategy(self.ontology)]

        # self.kase('Una piedra y un lápiz fueron encontrados en Argentina', '')
        self.kase('El funeral de Hugues que fue retransmitido de costa a costa, duró mucho tiempo.', 'Se retransmitió el funeral de Hugues que de costa a costa, duró mucho tiempo.')

        self.kase('En 2011, el gasoducto fue ideado, cuando Felipe Calderón aún era presidente de México y empezaban los destellos de el nuevo ‘ boom ’ energético de Estados Unidos.', 'Se ideó el gasoducto en 2011,  , cuando Felipe Calderón aún era presidente de México y empezaban los destellos de el nuevo ‘ boom ’ energético de Estados Unidos.')
        self.kase('Los edificios que están en la esquina serán demolidos.', 'Se demolerán los edificios que están en la esquina.')
        self.kase('Algunos muebles y otros objetos perdidos fueron encontrados en Maine.', 'Se encontraron algunos muebles y otros objetos perdidos en Maine.')
        self.kase('Dentro del país, miles de personas que no eran acordes con los parámetros raciales fueron esterilizadas en una treintena de Estados.', 'Dentro del país, miles de personas que no eran acordes con los parámetros raciales fueron esterilizadas en una treintena de Estados.')
        self.kase('Los temas han sido explicados antes.', 'Se explican los temas antes.')
        self.kase('Dijo que los temas han sido explicados antes.', 'Dijo que se explican los temas antes.')


        self.kase('La mujer había sido asesinada.', 'La mujer había sido asesinada.')

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
