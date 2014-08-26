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

        self.text = ("Fulano y Mengano. Telefónica mejoró gracias a su estrategia comercial."
                      "Estoy en la calle Florida."
                      "El Dr. Leandro Liptak murió." 
                      "El Juez Griesa murió."
                      "La empresa Adidas cerró. Muchos criticaron a la compañía Adidas."
                      "Fue a Sevilla, Cordoba y Madrid."
                      "El intendente de Buenos Aires murió."
                      "A diferencia de lo que sucedió en 2010, en Brasil no se hará presente la "
                      "ONG Hinchadas Unidas Argentinas, que nucleaba a las barras del fútbol argentino."
                      )
        paragraph = Paragraph.from_text(self.text)
        self.analyzer.analyze(paragraph)
        analysis = {'paragraph': paragraph} 
        self.processor = HyperlinkProcessor(analysis)

    def test__get_entities_from(self):
        for entity in self.processor.entities:
            self.assertTrue(entity.classification() != None )

        references = [x.referent.name() for x in self.processor.entities]
        self.assertEquals(sorted(references), sorted(list(set(references))))

    def test__get_gMaps_links(self):
        links = self.processor._get_gMaps_links()
        # print links
        expected = ['https://maps.google.com/maps?q=calle%20Florida', 
                    'https://maps.google.com/maps?q=Sevilla', 
                    'https://maps.google.com/maps?q=Madrid', 
                    'https://maps.google.com/maps?q=Cordoba', 
                    'https://maps.google.com/maps?q=Buenos_Aires']
        for x in expected:
            self.assertIn(x, links)

    def test__get_wikipedia_links(self):
        links = self.processor._get_wikipedia_links()
        print links
        expected = ['http://es.wikipedia.org/wiki/Telef%C3%B3nica', 
                    'http://es.wikipedia.org/wiki/Calle%20Florida', 
                    'http://es.wikipedia.org/wiki/Thomas%20P.%20Griesa',
                    'http://es.wikipedia.org/wiki/Adidas']
        for x in expected:
            self.assertIn(x, links)

    def test__get_other_links(self):
        links = self.processor._get_other_links()
        # print links
        expected = ['https://www.google.com.ar/search?q=ONG+Hinchadas+Unidas+Argentinas']
        for x in expected:
            self.assertIn(x, links)

    # Comentado para no hacer tantas searchs en Google            
    # def test__get_linkedIn_links(self):
    #     links = self.processor._get_linkedIn_<links()
    #     expected = [u'http://ar.linkedin.com/pub/leandro-liptak/95/36b/19b']
    #     for x in expected:
    #         self.assertIn(x, links)

if __name__ == '__main__':
    unittest.main()
