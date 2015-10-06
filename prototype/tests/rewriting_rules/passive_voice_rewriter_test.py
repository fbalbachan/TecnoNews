#!/usr/bin/env python
#-*- coding: utf-8 -*-
import unittest

from src.ling.freelingDictionaryParser import FreelingDictionaryParser
from src.model.paragraph.paragraph import Paragraph
from src.model.paragraph.paragraphAnalyzer import ParagraphAnalyzer
from src.model.sentence.sentenceAnalyzer import SentenceAnalyzer
from src.rewrite.rewriter import Rewriter
from src.rewrite.strategy.voicePassiveStrategy import VoicePassiveStrategy
from tests.freelingTreeRepository import FreelingTreeRepository


class TestRewriter(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        print "[Rewriter test]"

        self.sentenceAnalyzer = SentenceAnalyzer(FreelingTreeRepository("tests/input/trees"))
        self.analyzer = ParagraphAnalyzer(self.sentenceAnalyzer)

    def __(self):
        self.ontology = FreelingDictionaryParser.get_ontology()

    def test_dislocate_cite(self):
        self.strategies = [VoicePassiveStrategy(self.ontology)]

        self.kase('El acusado declaró: los noruegos habían sido conquistados por un inglés en 1066', 'El acusado declaró: Un inglés conquistaba a los noruegos en 1066')
        self.kase('Los noruegos habían sido conquistados por un inglés en 1066, pero yo fui sentenciado a muerte por el juez.','Un inglés conquistaba a los noruegos en 1066, pero el juez sentenció a muerte a mí.')
        self.kase('El hombre y la mujer fueron asesinados por otra persona', 'Otra persona asesinó al hombre y la mujer')
        self.kase('La mujer que vive al lado había sido asesinada por su marido.', 'Su marido asesinaba a la mujer que vive a el lado.')
        self.kase('Los noruegos fueron conquistados por alguien que dormía allí', 'Alguien que dormía allí conquistó a los noruegos')
        self.kase('El manuscrito que el pasado lunes fue hallado en el Mar Muerto por arqueólogos israelíes era falso', 'Arqueólogos israelíes el pasado lunes hallaron en el Mar Muerto el manuscrito que era falso')
        self.kase('El hombre comentó que el pasado lunes el manuscrito fue hallado en el Mar Muerto por arqueólogos israelíes', 'El hombre comentó que el pasado lunes arqueólogos israelíes hallaron en el Mar Muerto el manuscrito')

        self.kase('El hombre que era mi amigo había sido asesinado por Oswald', 'Oswald asesinaba al hombre que era mi amigo')
        self.kase('El noruego sabe que el no fue contagiado por los germenes del laboratorio.', 'El noruego sabe que el los germenes no contagiaron a él de el laboratorio.')
        self.kase('Los noruegos saben que ellos no fueron conquistados por los ingleses en el año 1066.', 'Los noruegos saben que los ingleses no conquistaron a ellos en el año 1066.')
        self.kase('Yo vi cuando el hombre ya había sido asesinado por la policía.', 'Yo vi cuando la policía ya asesinaba al hombre.')
        self.kase('El hombre ya fue asesinado por la policía.', 'La policía ya asesinó al hombre.')
        self.kase('La persona fue multada por la policía', 'La policía multó a la persona')
        self.kase('El hombre fue asesinado por la policía, aunque los robos habían sido denunciados por los vecinos',
                  'La policía asesinó al hombre , aunque los robos habían sido denunciados por los vecinos')
        self.kase('El hombre fue asesinado por la policía cuando los robos habían sido denunciados por los vecinos', 'La policía asesinó al hombre cuando los robos habían sido denunciados por los vecinos')

        self.kase('ella me dijo eso cuando los hombres habían sido arrestados por la policía', 'ella me dijo eso cuando la policía arrestaba a los hombres')
        self.kase('El hombre dijo que los prisioneros serán ejecutados mañana por el pelotón de fusilamiento', 'El hombre dijo que el pelotón de fusilamiento ejecutará mañana los prisioneros')
        self.kase('La mesa había sido construida con madera de Noruega.', 'La mesa había sido construida con madera de Noruega.')
        self.kase('La mujer había sido quemada por mi padre con madera de Noruega.', 'Mi padre quemaba a la mujer con madera de Noruega.')
        self.kase('La mesa había sido construida por mi padre con madera de Noruega.', 'Mi padre construía la mesa con madera de Noruega.')

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
