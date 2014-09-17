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
        # Con y sin coma inicial
        self.kase("Si yo amo a quien odia, soy libre", "Soy libre, si yo amo a quien odia")
        self.kase("Si yo amo a quien odia soy libre",  "Soy libre, si yo amo a quien odia")

        # Si p, q sólo es unidireccional
        # TODO: Fix 'Tokenization error!'
        #self.kase("Soy libre si yo amo a quien odia",  "Soy libre si yo amo a quien odia")
        self.kase("Si pasa esto, ocurre esto",  "Ocurre esto, si pasa esto")
        self.kase("Ocurre esto, si pasa esto",  "Ocurre esto, si pasa esto")

        # Cuando/apenas p, q <==> q, cuando/apenas p
        # Con/sin comas intermedias; con/sin puntuación final
        self.kase("Cuando pasa esto, ocurre esto.", "Ocurre esto, cuando pasa esto.")
        self.kase("Apenas pasa esto ocurre esto", "Ocurre esto, apenas pasa esto")
        self.kase("Ocurre esto cuando pasa esto.", "Cuando pasa esto, ocurre esto.")
        self.kase("Ocurre esto, apenas pasa esto", "Apenas pasa esto, ocurre esto")

        # Apenas como adverbio no se tiene en cuenta
        self.kase("La sopa está apenas salada", "La sopa está apenas salada")
        self.kase("La sopa está apenas vuelva", "Apenas vuelva, la sopa está")

        # Múltiples oraciones
        self.kase(
            "Si yo amara a quien odió sería libre. Si yo odio a quien ama, soy esclavo.",
            "Sería libre, si yo amara a quien odió. Soy esclavo, si yo odio a quien ama."
        )

        # Minúscula
        self.kase("si yo soy minúscula, vos dejame en minúscula", "vos dejame en minúscula, si yo soy minúscula")

        # Con aclaración entre comas
        self.kase("Si Cristina, la presidenta, hace esto, eso ocurre.", "Eso ocurre, si Cristina, la presidenta, hace esto.")

        # En caso de, y siempre y cuando
        #self.kase("En caso de que duerma, los sueños son posibles", "Los sueños son posibles, en caso de que duerma")
        #self.kase("En caso de dormir, los sueños son posibles", "Los sueños son posibles, en caso de dormir")
        #self.kase("Siempre y cuando yo duerma, los sueños son posibles", "Los sueños son posibles, siempre y cuando yo duerma")
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

        self.strategies = None # Estrategias por defecto
        self.kase("Si odiase a quien pudo ver la luz, amaré", "Voy a amar, si odiara a quien ha podido ver la luz")

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
