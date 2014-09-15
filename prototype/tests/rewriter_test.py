#!/usr/bin/env python
#-*- coding: utf-8 -*-
import unittest

from src.ling.freelingDictionaryParser import FreelingDictionaryParser
from src.model.paragraph.paragraph import Paragraph
from src.model.paragraph.paragraphAnalyzer import ParagraphAnalyzer
from src.model.sentence.sentenceAnalyzer import SentenceAnalyzer
from src.rewrite.rewriter import Rewriter
from tests.freelingTreeRepository import FreelingTreeRepository

from src.rewrite.strategy.adverbialClauseDislocationStrategy import AdverbialClauseDislocationStrategy
from src.rewrite.strategy.futureStrategy import FutureStrategy
from src.rewrite.strategy.pastSimpleToCompoundStrategy import PastSimpleToCompoundStrategy
from src.rewrite.strategy.subjuntiveImperfectStrategy import SubjuntiveImperfectStrategy
from src.rewrite.strategy.verbalSynStrategy import VerbalSynStrategy

class TestClauseAnalyzer(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        print "[Rewriter test]"

        self.sentenceAnalyzer = SentenceAnalyzer(FreelingTreeRepository("tests/input/trees"))
        self.analyzer = ParagraphAnalyzer(self.sentenceAnalyzer)

    def __(self):
        ontology = FreelingDictionaryParser.from_resource()
        print ontology.get_lexical_form("haber", { "mode" : "indicative", "time" : "presente", "person" : 2, "number" : "singular"})

    def test_adverbial_clause_dislocation(self):
        self.strategies = [AdverbialClauseDislocationStrategy()]
        # TODO: Funcionaría al arreglar +1 de offset en AdverbialClauseDislocationStrategy.
        # self.kase("Si yo amara a quien odió sería libre. Si yo odio a quien ama, soy esclavo.", "Sería libre, si yo amara a quien odió. Soy esclavo, si yo odio a quien ama.")
        self.kase("Si yo amo a quien odia soy libre", "Soy libre, si yo amo a quien odia")
        self.kase("Si yo amo a quien odia, soy libre", "Soy libre, si yo amo a quien odia")

    def test_past_simple_to_compound(self):
        self.strategies = [PastSimpleToCompoundStrategy(self.ontology)]
        self.kase("Leandro amó", "Leandro ha amado")
        self.kase("Yo amé", "Yo he amado")
        self.kase("Tú amaste", "Tú has amado")
        self.kase("Él sanó", "Él ha sanado")
        self.kase("Ellas miraron", "Ellas han mirado")

        self.kase("Nosotros pudimos curar", "Nosotros hemos podido curar")
        self.kase("Yo quise amar", "Yo he querido amar")
        self.kase("José intentó sanar", "José ha intentado sanar")

        # Mayúsculas si las había en el verbo original
        self.kase("Amé a María", "He amado a María")

        # Ya es compuesto
        self.kase("Yo había querido amar", "Yo había querido amar")

        # Es una locución
        self.kase("Yo metí la pata", "Yo metí la pata")

    def test_subjuntive_imperfect(self):
        self.strategies = [SubjuntiveImperfectStrategy(self.ontology)]
        self.kase("Si yo muriese sería feliz", "Si yo muriera sería feliz")
        self.kase("Si muriéramos estaría bien", "Si muriésemos estaría bien")

    def test_future(self):
        self.strategies = [FutureStrategy(self.ontology)]
        self.kase("Moriré mañana", "Voy a morir mañana")
        self.kase("Construiremos más viviendas", "Vamos a construir más viviendas")
        self.kase("Juan amará", "Juan va a amar")

    def test_combined(self):
        self.strategies = [PastSimpleToCompoundStrategy(self.ontology), SubjuntiveImperfectStrategy(self.ontology), FutureStrategy(self.ontology) ]
        self.kase("Si yo amara a quien odió sería libre", "Si yo amase a quien ha odiado sería libre")
        self.kase("Amaré si odiase a quien pudo ver la luz", "Voy a amar si odiara a quien ha podido ver la luz")

        # TODO: Funcionaría al arreglar +1 de offset en AdverbialClauseDislocationStrategy.
        #self.strategies = None # Estrategias por defecto
        #self.kase("Amaré si odiase a quien pudo ver la luz", "Si odiara a quien ha podido ver la luz, voy a amar")

    def kase(self, source, edited):
        print "Case:", source
        analyzer = self.analyzer

        paragraph = Paragraph.from_text(source)
        analyzer.analyze(paragraph)

        text = Rewriter(paragraph, self.ontology, self.strategies).rewrite()
        print "\t[SOURCE]", paragraph.text
        print "\t[EDITED]", text

        self.assertEqual(text, edited)
    
    ontology = FreelingDictionaryParser.from_resource()

if __name__ == '__main__':
    unittest.main()
