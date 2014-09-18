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
        self.kase("Leandro amó a María", ("Leandro", 1) , ("María", 0.5))
        self.kase("José compró para Juan", ("José", 1) , ("Juan", 0.5))
        self.kase("Leandro desconfió de Gustavo", ("Leandro", 1) , ("Gustavo", 0.5))
        #self.kase("Los noruegos son un pueblo agresivo", ("Los noruegos", 1) , ("un pueblo agresivo", 0.5))
        self.kase("Pedro vivió en Caracas", ("Pedro", 1) , ("Caracas", 0.25))
        self.kase("Pedro vivió en Caracas", ("Pedro", 1) , ("Caracas", 0.25))
        self.kase("Pedro jugó con María", ("Pedro", 1) , ("María", 0.25))

        self.kase("Leandro amó a María, y María amó a José", ("María", 1.5) , ("Leandro", 1), ("José", 0.5))
        self.kase("Pedro jugó con María quien vivió en Caracas", ("María", 1.25), ("Pedro", 1), ("Caracas", 0.25))
        self.kase("Pedro amó a Maria. Dijo que la amaba.", ("Pedro", 3), ("Maria", 1))

        self.kase("La empresa de Leandro compró a la empresa de María", ("Leandro", 1), ("María", 0.5))

    def kase(self, text, *expected):
        paragraph = Paragraph.from_text(text)
        self.analyzer.analyze(paragraph)
        EntityUnifier(paragraph).unify()
        ranking = ReferentRanker(paragraph).rank()

        actual = [ (referent.name(), score) for referent, score in ranking ]
        self.assertEqual(actual, list(expected))

if __name__ == '__main__':
    unittest.main()