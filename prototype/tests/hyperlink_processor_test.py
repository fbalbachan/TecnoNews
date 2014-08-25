# -*- coding: utf-8 -*-

import unittest
import wikipedia as wk

from src.model.paragraph.paragraph import Paragraph
from src.model.sentence.sentenceAnalyzer import SentenceAnalyzer
from src.model.paragraph.paragraphAnalyzer import ParagraphAnalyzer
from src.sentinews.hyperlink_processor import HyperlinkProcessor
from tests.freelingTreeRepository import FreelingTreeRepository

class TestHyperLinkProcessor(unittest.TestCase):

    def setUp(self):
        self.analyzer = ParagraphAnalyzer(SentenceAnalyzer(FreelingTreeRepository("tests/input/trees")))

        self.texts = ('Fulano y Mengano',
                      'Telefónica mejoró gracias a su estrategia comercial', 
                      'Estoy en la calle Florida',
                      'El Dr. Leandro Liptak murió', 
                      'El Juez Griesa murió')

        #TODO: A falta de un repository de parrafos, armo muchos processors con cada oracion
        #      y los testeo todos.
        self.processors = []

        for sentence in self.texts:
            paragraph = Paragraph.from_text(sentence)
            self.analyzer.analyze(paragraph)
            analysis = {'paragraph': paragraph} 
            self.processors.append(HyperlinkProcessor(analysis))

    def test__get_entities_from(self):
        # "Fulano y Mengano" no forman un entity interesante
        # Todas las demas, tienen un entity

        self.assertEquals(len(self.processors[0].entities), 0)
        self.assertEquals(len(self.processors[1].entities), 1)
        self.assertEquals(len(self.processors[2].entities), 1)
        self.assertEquals(len(self.processors[3].entities), 1)
        self.assertEquals(len(self.processors[4].entities), 1)

    def test__get_wikipedia_links(self):
        links = []
        for p in self.processors:
            links += p._get_wikipedia_links()
        expected = ['http://es.wikipedia.org/wiki/Telef%C3%B3nica', 
                    'http://es.wikipedia.org/wiki/Calle%20Florida', 
                    'http://es.wikipedia.org/wiki/Thomas%20P.%20Griesa']

        self.assertEquals(len(expected), len(links))
        for x in expected:
            self.assertIn(x, links)

if __name__ == '__main__':
    unittest.main()
