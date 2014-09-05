#!/usr/bin/env python
#-*- coding: utf-8 -*-
import unittest

from src.model.paragraph.paragraph import Paragraph
from src.model.paragraph.paragraphAnalyzer import ParagraphAnalyzer
from src.model.sentence.sentenceAnalyzer import SentenceAnalyzer
from src.rewrite.rewriter import Rewriter
from tests.freelingTreeRepository import FreelingTreeRepository


class TestClauseAnalyzer(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        print "[Rewriter test]"

        self.sentenceAnalyzer = SentenceAnalyzer(FreelingTreeRepository("tests/input/trees"))
        self.analyzer = ParagraphAnalyzer(self.sentenceAnalyzer)

    def test(self):
        analyzer = self.analyzer

        paragraph = Paragraph.from_text("Leandro murió en silencio.")
        analyzer.analyze(paragraph)

        text = Rewriter(paragraph).rewrite()
        print "[SOURCE]", paragraph.text
        print "[EDITED]", text

if __name__ == '__main__':
    unittest.main()
