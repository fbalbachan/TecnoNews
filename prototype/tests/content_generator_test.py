#!/usr/bin/env python
#-*- coding: utf-8 -*-

import unittest

from src.extension.wikipediaContentGenerator import WikipediaContentGenerator
from src.model.paragraph.paragraph import Paragraph
from src.model.paragraph.paragraphAnalyzer import ParagraphAnalyzer
from src.model.referent.entityUnifier import EntityUnifier
from src.model.referent.referentInformationExtractor import ReferentInformationExtractor
from src.model.referent.referentRanker import ReferentRanker
from src.model.sentence.sentenceAnalyzer import SentenceAnalyzer
from tests.freelingTreeRepository import FreelingTreeRepository


class ContentGeneratorTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        print "[Content generator test]"

        self.sentenceAnalyzer = SentenceAnalyzer(FreelingTreeRepository("tests/input/news/trees"))
        self.analyzer = ParagraphAnalyzer(self.sentenceAnalyzer)

    def test(self):
        paragraph = Paragraph.from_text(open("tests/input/news/higgs.txt").read())
        self.analyzer.analyze(paragraph)

        EntityUnifier(paragraph).unify()
        ReferentInformationExtractor.update_named_referents_of(paragraph)

        ranking = ReferentRanker(paragraph).rank()

        analysis = { "paragraph" : paragraph, "referent_ranking" : ranking }

        WikipediaContentGenerator(analysis).generate()

if __name__ == '__main__':
    unittest.main()