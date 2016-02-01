# -*- coding: utf-8 -*-

import unittest
import wikipedia as wk

from src.model.paragraph.paragraph import Paragraph
from src.model.sentence.sentenceAnalyzer import SentenceAnalyzer
from src.model.paragraph.paragraphAnalyzer import ParagraphAnalyzer
from src.sentinews.hyperlink_processor import HyperlinkProcessor
from tests.freelingTreeRepository import FreelingTreeRepository
from src.model.sentilecto import Sentilecto

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
                      "El médico Maurice Ohayon."
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
        self.processor._get_gMaps_links()
        expected = ['https://maps.google.com/maps?q=calle%20Florida', 
                    'https://maps.google.com/maps?q=Sevilla', 
                    'https://maps.google.com/maps?q=Madrid', 
                    'https://maps.google.com/maps?q=Cordoba', 
                    'https://maps.google.com/maps?q=Buenos_Aires']
        for x in expected:
            self.assertIn(x, self._get_links_from_processor())

    def test__get_wikipedia_links(self):
        self.processor._get_wikipedia_links()
        expected = ['http://es.wikipedia.org/wiki/Telef%C3%B3nica', 
                    'http://es.wikipedia.org/wiki/Calle%20Florida', 
                    'http://es.wikipedia.org/wiki/Thomas%20P.%20Griesa',
                    'http://es.wikipedia.org/wiki/Adidas']
        for x in expected:
            self.assertIn(x, self._get_links_from_processor())

    def test__get_linkedIn_links(self):
        self.processor._get_linkedIn_links()
        expected = [u'http://ar.linkedin.com/pub/leandro-liptak/95/36b/19b', 
                    u'http://www.linkedin.com/pub/maurice-ohayon/1b/6b3/516']
        for x in expected:
            self.assertIn(x, self._get_links_from_processor())

    def test__get_other_links(self):
        self.processor._get_other_links()
        expected = ['https://www.google.com.ar/search?q=ONG+Hinchadas+Unidas+Argentinas']
        for x in expected:
            self.assertIn(x, self._get_links_from_processor())

    def test__merge_entities(self):
        text = ("Si Leandro Liptak no quiere estelarizar otra película de Cazafantasmas,"
                " quizás pueda ser el director de casting. En su aparición en el Festival"
                " de Cine Internacional de Toronto, Liptak habló sobre el rumor de una nueva"
                " película de la saga con mujeres como estelares, que el estudio Sony"
                " está considerando.")
        processor = HyperlinkProcessor(Sentilecto.analyze(text))
        self.assertIn('Leandro_Liptak', [str(e) for e in processor.entities])
        test_entity = [e for e in processor.entities if e.name() == 'Leandro_Liptak'][0]
        processor.links_by_entity[test_entity]['linkedin'] = 'http://www.google.com'
        tagged_text = processor._add_links_to_text()
        self.assertIn("<a id='e_0' href=http://www.google.com target=_blank>Leandro Liptak</a>", tagged_text)
        self.assertIn(" <a id='e_1' href=http://www.google.com target=_blank>Liptak</a>", tagged_text)

    def _get_links_from_processor(self):
        res = []
        for links_by_type in self.processor.links_by_entity.values():
            for links in links_by_type.values():
                res.append(links) 
        return res

if __name__ == '__main__':
    unittest.main()
