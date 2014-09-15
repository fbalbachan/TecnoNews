#!/usr/bin/env python
#-*- coding: utf-8 -*-

import unittest

from src.model.paragraph.paragraph import Paragraph
from src.model.paragraph.paragraphAnalyzer import ParagraphAnalyzer
from src.model.referent.entityUnifier import EntityUnifier
from src.model.referent.referentRanker import ReferentRanker
from src.model.sentence.sentenceAnalyzer import SentenceAnalyzer
from tests.freelingTreeRepository import FreelingTreeRepository


class ReferentRankerTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        print "[Referent ranking test]"

        self.sentenceAnalyzer = SentenceAnalyzer(FreelingTreeRepository("tests/input/trees"))
        self.analyzer = ParagraphAnalyzer(self.sentenceAnalyzer)

    def test(self):
        self.kase("Leandro amó a María", ("Leandro", 1) , ("María", 0.75))
        self.kase("José compró para Juan", ("José", 1) , ("Juan", 0.75))
        self.kase("Leandro desconfió de Gustavo", ("Leandro", 1) , ("Gustavo", 0.75))
        self.kase("Los noruegos son un pueblo agresivo", ("Los noruegos", 1) , ("un pueblo agresivo", 0.75))
        self.kase("Pedro vivió en Caracas", ("Pedro", 1) , ("Caracas", 0.5))
        self.kase("Pedro vivió en Caracas", ("Pedro", 1) , ("Caracas", 0.5))
        self.kase("Pedro jugó con María", ("Pedro", 1) , ("María", 0.5))

        self.kase("Leandro amó a María, y María amó a José", ("María", 1.75) , ("Leandro", 1), ("José", 0.75))
        self.kase("Pedro jugó con María quien vivió en Caracas", ("María", 1.5), ("Pedro", 1), ("Caracas", 0.5))
        self.kase("Pedro amó a Maria. Dijo que la amaba.", ("Pedro", 3), ("Maria", 1.5))

        # TODO: Ordenar los referentes ante empate, para así poder testear. El test en sí funciona: reciben el mismo
        # score las entidades de nivel superior que las subordinadas, de acuerdo con la función sintáctica.

        #self.kase("La empresa de Leandro compró a la empresa de María", ("La empresa de Leandro", 1), ("Leandro", 1),
        #          ("Maria", 0.75), ("la empresa de María", 0.75))

    def kase(self, text, *expected):
        paragraph = Paragraph.from_text(text)
        self.analyzer.analyze(paragraph)
        EntityUnifier(paragraph).unify()
        ranking = ReferentRanker(paragraph).rank()

        actual = [ (referent.name(), score) for referent, score in ranking ]
        self.assertEqual(actual, list(expected))

if __name__ == '__main__':
    unittest.main()