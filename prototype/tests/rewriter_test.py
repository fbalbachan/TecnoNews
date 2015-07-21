#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest

from src.ling.freelingDictionaryParser import FreelingDictionaryParser
from src.ling.numberEnum import NumberEnum
from src.model.paragraph.paragraph import Paragraph
from src.model.paragraph.paragraphAnalyzer import ParagraphAnalyzer
from src.model.sentence.sentenceAnalyzer import SentenceAnalyzer
from src.rewrite.rewriter import Rewriter
from src.rewrite.strategy.adverbialClauseDislocationStrategy import AdverbialClauseDislocationStrategy
from src.rewrite.strategy.segunToDijoDislocationStrategy import SegunToDijoDislocationStrategy
from src.rewrite.strategy.althoughClauseDislocationStrategy import AlthoughClauseDislocationStrategy
from src.rewrite.strategy.dateTimeStrategy import DateTimeStrategy
from src.rewrite.strategy.futureToGoConstructionStrategy import FutureToGoConstructionStrategy
from src.rewrite.strategy.modalDeberToTieneQue import ModalDeberToTieneQue
from src.rewrite.strategy.pastSimpleToCompoundStrategy import PastSimpleToCompoundStrategy
from src.rewrite.strategy.subjunctiveImperfectStrategy import SubjunctiveImperfectStrategy
from src.rewrite.strategy.synonymsStrategy import SynonymsStrategy
from src.rewrite.strategy.tieneQueToModalDeber import TieneQueToModalDeber
from tests.freelingTreeRepository import FreelingTreeRepository


class TestRewriter(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        print "[Rewriter test]"

        self.sentenceAnalyzer = SentenceAnalyzer(FreelingTreeRepository("tests/input/trees"))
        self.analyzer = ParagraphAnalyzer(self.sentenceAnalyzer)

    def __(self):
        ontology = FreelingDictionaryParser.from_resource()
        msi = {"mode": "indicative", "time": "presente", "person": 2, "number": NumberEnum.singular}
        print ontology.get_lexical_form("haber", msi)

    def test_segun_to_dijo_dislocation(self):
        self.strategies = [SegunToDijoDislocationStrategy([True], [""])]

        # Sin comillas no cambia
        self.kase('Según Pedro esto es así.', 'Según Pedro esto es así.')

        #=================================================
        # CON Dislocación, SIN cambio a "de acuerdo con"
        # Diferentes opciones de puntuación
        self.kase('Según Pedro "esto es así"', '"Esto es así", según Pedro')
        self.kase('Según Pedro, "esto es así"', '"Esto es así", según Pedro')
        self.kase('Según Pedro "esto es así".', '"Esto es así", según Pedro.')
        self.kase('Según Pedro, "esto es así".', '"Esto es así", según Pedro.')
        # Múltiples oraciones / minúsculas
        self.kase(
            'Según Pedro, "nada pasa". según él, "estaría bueno". Según mi imaginación, "es impresionante"',
            '"Nada pasa", según Pedro. "estaría bueno", según él. "Es impresionante", según mi imaginación',
        )

        #=================================================
        # CON Dislocación, CON cambio a "de acuerdo con"
        self.strategies = [SegunToDijoDislocationStrategy([True], ["de_acuerdo_con"])]
        # Diferentes opciones de puntuación
        self.kase('Según Pedro "esto es así"', '"Esto es así", de acuerdo con Pedro')
        self.kase('Según Pedro, "esto es así"', '"Esto es así", de acuerdo con Pedro')
        self.kase('Según Pedro "esto es así".', '"Esto es así", de acuerdo con Pedro.')
        self.kase('Según Pedro, "esto es así".', '"Esto es así", de acuerdo con Pedro.')
        # Múltiples oraciones / minúsculas
        self.kase(
            'Según Pedro, "nada pasa". según él, "estaría bueno". Según mi imaginación, "es impresionante"',
            '"Nada pasa", de acuerdo con Pedro. "estaría bueno", de acuerdo con él. "Es impresionante", de acuerdo con mi imaginación',
        )

        #=================================================
        # SIN Dislocación, CON cambio a "de acuerdo con"
        self.strategies = [SegunToDijoDislocationStrategy([False], ["de_acuerdo_con"])]
        # Diferentes opciones de puntuación
        self.kase('Según Pedro "esto es así"', 'De acuerdo con Pedro "esto es así"')
        self.kase('Según Pedro, "esto es así"', 'De acuerdo con Pedro, "esto es así"')
        self.kase('Según Pedro "esto es así".', 'De acuerdo con Pedro "esto es así".')
        self.kase('Según Pedro, "esto es así".', 'De acuerdo con Pedro, "esto es así".')
        # Múltiples oraciones / minúsculas
        self.kase(
            'Según Pedro, "nada pasa". según él, "estaría bueno". Según mi imaginación, "es impresionante"',
            'De acuerdo con Pedro, "nada pasa". de acuerdo con él, "estaría bueno". De acuerdo con mi imaginación, "es impresionante"',
        )

    def test_although_clause_dislocation(self):
        self.strategies = [AlthoughClauseDislocationStrategy()]

        # Malformaciones o "aunque" sin tesis
        self.kase("Duermo aunque", "Duermo aunque")
        self.kase("Aunque duermo", "Aunque duermo")

        # Diferentes opciones de puntuación
        self.kase("Aunque duerma sigo pensando", "Sigo pensando, aunque duerma")
        self.kase("Aunque duerma, sigo pensando", "Sigo pensando, aunque duerma")
        self.kase("Aunque duerma sigo pensando.", "Sigo pensando, aunque duerma.")
        self.kase("Aunque duerma, sigo pensando.", "Sigo pensando, aunque duerma.")

        self.kase("Sigo pensando aunque duerma", "Aunque duerma, sigo pensando")
        #self.kase("Sigo pensando, aunque duerma",  "Aunque duerma, sigo pensando")
        self.kase("Sigo pensando aunque duerma.",  "Aunque duerma, sigo pensando.")
        #self.kase("Sigo pensando, aunque duerma.",  "Aunque duerma, sigo pensando.")

        # A pesar de que
        self.kase("A pesar de que odie, soy libre.",  "Soy libre, a pesar de que odie.")
        self.kase("Soy libre, a pesar de que odie.",  "A pesar de que odie, soy libre.")

        # Pese a que
        self.kase("Pese a que odia, soy libre.",  "Soy libre, pese a que odia.")
        self.kase("Soy libre, pese a que odia.",  "Pese a que odia, soy libre.")

        # Múltiples oraciones
        self.kase(
            "Aunque me amara sería libre. a pesar de que ame, soy esclavo. Siempre pienso, pese a que duerma",
            "Sería libre, aunque me amara. soy esclavo, a pesar de que ame. Pese a que duerma, siempre pienso"
        )

        # Minúscula
        self.kase("aunque odie soy libre", "soy libre, aunque odie")
        self.kase("soy libre pese a que odie", "pese a que odie, soy libre")

        # Casos reales
        #self.kase(
        #    "El periódico ha señalado que el riesgo de hacerse adicto comiendo los fideos es prácticamente inexistente, aunque se comen de forma continua durante un largo periodo.",
        #    "Aunque se comen de forma continua durante un largo periodo, el periódico ha señalado que el riesgo de hacerse adicto comiendo los fideos es prácticamente inexistente."
        #)

    def test_adverbial_clause_dislocation_no_header_change(self):
        self.strategies = [AdverbialClauseDislocationStrategy(self.ontology, False)]

        # Con y sin coma inicial
        self.kase("Si yo amo a quien odia, soy libre", "Soy libre, si yo amo a quien odia")
        self.kase("Si yo amo a quien odia soy libre",  "Soy libre, si yo amo a quien odia")

        # Si p, q sólo es unidireccional
        # TODO: Fix 'Tokenization error!'
        #self.kase("Soy libre si yo amo a quien odia",  "Soy libre si yo amo a quien odia")
        self.kase("Si pasa esto, ocurre esto",  "Ocurre esto, si pasa esto")
        self.kase("Ocurre esto, si pasa esto",  "Si pasa esto, ocurre esto")

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

        # Una vez que
        self.kase("Una vez que yo sea así, lo lograré.", "Lo lograré, una vez que yo sea así.")
        self.kase("Lo lograré, una vez que sea así", "Una vez que sea así, lo lograré")

        # Mientras
        self.kase("Mientras él está allá, ella está acá.", "Ella está acá, mientras él está allá.")
        self.kase("Ella está acá mientras él está allá.", "Mientras él está allá, ella está acá.")
        # TODO: Por ahora mientras es unidireccional ya que ", mientras" separa en oraciones.
        #self.kase("Ella está acá, mientras él está allá.", "Mientras él está allá, ella está acá.")

        # Según
        self.kase("Según dijo Pedro, ella está acá.", "Ella está acá, según dijo Pedro.")
        self.kase("Ella está acá, según dijo Pedro.", "Según dijo Pedro, ella está acá.")

        # PORQUE no es dislocable
        self.kase("Porque yo soy así, ella es así.", "Porque yo soy así, ella es así.")
        self.kase("Ella es así, porque yo soy así", "Ella es así, porque yo soy así")

        # QUE incluyente no es dislocable
        self.kase("Yo digo que esto es así.", "Yo digo que esto es así.")
        self.kase("Que esto es así, yo digo.", "Que esto es así, yo digo.")

        # En caso de que (unidireccional)
        # TODO: Terminar de adaptar "en caso de que" a la recursividad!!
        #self.kase(
        #    "probando mayúscula de oración y con múltiples oraciones. En caso de que yo sea rico, me compro un yate. listo.",
        #    "probando mayúscula de oración y con múltiples oraciones. Me compro un yate, en caso de que yo sea rico. listo."
        #)
        #self.kase("en caso de que duerma, los sueños son posibles", "los sueños son posibles, en caso de que duerma")
        #self.kase("Los sueños son posibles, en caso de que duerma.", "Los sueños son posibles, en caso de que duerma.")

        # En caso de (sin "que" queda igual)
        self.kase("En caso de dormir, los sueños son posibles", "En caso de dormir, los sueños son posibles")

        # Algunos casos reales
        self.kase(
            "Si enciendes la televisión cualquier día de la semana, es probable que te topes con la repetición de algún episodio de Friends.",
            "Es probable que te topes con la repetición de algún episodio de Friends, si enciendes la televisión cualquier día de la semana."
        )
        self.kase(
            "Si no ha sido tu día —ni tu año— puedes contar con un grupo selecto de amigos que te van a hacer sonreír.",
            "Puedes contar con un grupo selecto de amigos que te van a hacer sonreír, si no ha sido tu día —ni tu año—."
        )
        self.kase(
            "Si estás viendo esta nota en tu móvil, mira aquí la galería.",
            "Mira aquí la galería, si estás viendo esta nota en tu móvil."
        )
        self.kase(
            "La película de 2013 ha sido increíblemente popular en la taquilla que fue a verla cuando Disney estrenó el film.",
            "La película de 2013 ha sido increíblemente popular en la taquilla que cuando Disney estrenó el film, fue a verla."
        )

        #self.kase("Siempre y cuando yo duerma, los sueños son posibles", "Los sueños son posibles, siempre y cuando yo duerma")

    def test_adverbial_clause_dislocation_header_change(self):
        self.strategies = [AdverbialClauseDislocationStrategy(self.ontology)]

        self.kase("Si yo amo a quien odia, soy libre", "Soy libre, en caso de que yo ame a quien odia")
        self.kase("Si quiero comer, ocurre esto",  "Ocurre esto, en caso de que quiera comer")
        self.kase("Si yo tomé esto, ocurre esto",  "Ocurre esto, en caso de que yo haya tomado esto")
        self.kase("Si yo pude comer esto, ocurre esto",  "Ocurre esto, en caso de que yo haya podido comer esto")
        self.kase("Si tomaron esto, ocurre esto",  "Ocurre esto, en caso de que hayan tomado esto")
        self.kase("Si tomamos esto, ocurre esto",  "Ocurre esto, en caso de que tomemos esto")
        self.kase("Si yo tomase esto, ocurre esto",  "Ocurre esto, si yo tomase esto")
        self.kase("Si yo tomara esto, ocurre esto",  "Ocurre esto, si yo tomara esto")
        self.kase("Ocurre esto, si pasa esto",  "En caso de que pase esto, ocurre esto")
        self.kase("Si los átomos chocaban, explotaba todo.",  "Explotaba todo, en caso de que los átomos chocaran.")
        self.kase("Si los átomos chocarán, explotará.",  "Explotará, en caso de que los átomos chocaren.")

        # apenas -> cuando (unidireccional)
        self.kase("Apenas pasa esto, ocurre esto.", "Ocurre esto, cuando pasa esto.")
        self.kase("Ocurre esto apenas pasa esto.", "Cuando pasa esto, ocurre esto.")
        self.kase("ocurre esto, apenas pasa esto", "cuando pasa esto, ocurre esto")
        self.kase("Cuando pasa esto, ocurre esto.", "Ocurre esto, cuando pasa esto.")

        # Por ahora sin soporte de verbos inicialmente compuestos
        self.kase("Si ella había tomado esto, ocurre esto",  "Ocurre esto, si ella había tomado esto")
        self.kase("Si ella ha tomado esto, ocurre esto",  "Ocurre esto, si ella ha tomado esto")

        # Combinado
        self.kase(
            "Si amara a quien odió sería libre. Si odié a quien ama, soy esclavo. Apenas corro, me libero.",
            "Sería libre, si amara a quien odió. Soy esclavo, en caso de que haya odiado a quien ama. Me libero, cuando corro."
        )

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

    def test_modal_deber_to_tiene_que(self):
        self.strategies = [ModalDeberToTieneQue(self.ontology)]
        self.kase("Yo debo amar a todos", "Yo tengo que amar a todos")
        self.kase("Yo debí amar a todos", "Yo tuve que amar a todos")

    def test_tiene_que_to_modal_deber(self):
        self.strategies = [TieneQueToModalDeber(self.ontology)]
        self.kase("Yo tuve que amar a todos", "Yo debí amar a todos")
        self.kase("Tendré que buscar agua", "Deberé buscar agua")
        self.kase("Tendría que buscar agua", "Debería buscar agua")

    def test_subjunctive_imperfect(self):
        self.strategies = [SubjunctiveImperfectStrategy(self.ontology)]
        self.kase("Si yo muriese sería feliz", "Si yo muriera sería feliz")
        self.kase("Si muriéramos estaría bien", "Si muriésemos estaría bien")

    def test_future(self):
        self.strategies = [FutureToGoConstructionStrategy(self.ontology)]
        self.kase("Moriré mañana", "Voy a morir mañana")
        self.kase("Construiremos más viviendas", "Vamos a construir más viviendas")
        self.kase("Juan amará", "Juan va a amar")

    def test_synonyms(self):
        self.strategies = [SynonymsStrategy(self.ontology)]
        self.kase("Semanalmente", "Cada semana")
        self.kase("A la vez", "A el mismo tiempo") # Prioridad sinónimos
        self.kase("Desagradablemente", "Dolorosamente")

        self.kase("El rey construyó su victoria en base a mentiras",
                  "El rey edificó su victoria en base a mentiras")
        self.kase("Para el alumno, memorizar el alfabeto es un reto absurdo",
                  "Para el alumno, memorizar el abecedario es un desafío ilógico")
        self.kase("El principio del famoso robo fue maravilloso y rápido",
                  "El comienzo del famoso robo fue extraordinario y rápido")
        self.kase("Quizás salga primero a pesar de esperar de vez en cuando",
                  "Tal vez parta primero pese a esperar esporádicamente")
        self.kase("Tal vez salga primero pese a esperar esporádicamente",
                  "Quizás parta primero a pesar de esperar de vez en cuando")

    def test_combined(self):
        self.strategies = [SynonymsStrategy(self.ontology), PastSimpleToCompoundStrategy(self.ontology), SubjunctiveImperfectStrategy(self.ontology), \
                           FutureToGoConstructionStrategy(self.ontology) ]
        self.kase("Si yo amara a quien odió sería libre", "Si yo amase a quien ha odiado sería libre")
        self.kase("Amaré si odiase a quien pudo ver la luz", "Voy a amar si odiara a quien pudo observar la luz")

        self.strategies = None # Estrategias por defecto
        self.kase("Si odiase a quien pudo ver la luz, amaré", "Voy a amar, si odiara a quien pudo observar la luz")

    def test_datetime(self):
        self.strategies = [DateTimeStrategy(self.ontology)]

        self.kase("En 2010, jugó al fútbol.", "Jugó a el fútbol, en 2010.")
        self.kase("El 15 de Agosto, Leandro jugó al fútbol.", "Leandro jugó a el fútbol, el 15 de Agosto.")
        self.kase("Murió en la semana de mayo, honradamente.", "En la semana de mayo, murió, honradamente.")
        self.kase("Murió en la semana de mayo, honradamente, en la madrugada.", "En la semana de mayo, en la madrugada, murió, honradamente.")
        self.kase("En 1990 falleció, luego del otoño, honradamente, a la madrugada.", "Luego de el otoño, a la madrugada, falleció honradamente, en 1990.")
        self.kase("En 2010 falleció el hombre que había nacido en 1880.", "Falleció el hombre que había nacido en 1880, en 2010.")
        self.kase('En abril de 2012, Hillary Clinton le dijo a ABC que "dependía realmente de ella si ganaría el título de abuela", pero añadió: "Me gustaría tenerlo... creo que sería muy bueno".', \
                  'Hillary Clinton le dijo a ABC que " dependía realmente de ella si ganaría el título de abuela ", en abril de 2012, pero añadió: "Me gustaría tenerlo... creo que sería muy bueno".')
        self.kase('"Amó en 2013 a su hermana"', '"En 2013, amó a su hermana"')

        # Time reference en subordinada
        self.kase("El hombre que en 2010 había nacido murió", "El hombre que en 2010 había nacido murió")

        # En coordinada
        self.kase("En 2010 jugó y lloró en primavera", "Jugó, en 2010 y lloró en primavera")
        self.kase("Jugó y lloró en primavera", "Jugó y en primavera, lloró")

        self.kase("Corrió a 10 kilómetros por hora", "Corrió a 10 kilómetros por hora")
        self.kase("Pasó esto hace una hora", "Hace una hora, pasó esto")

    def kase(self, source, edited):
        print "Case:", source
        analyzer = self.analyzer

        paragraph = Paragraph.from_text(source)
        analyzer.analyze(paragraph)

        text = Rewriter(paragraph, self.ontology, self.strategies).rewrite()
        print "\t[SOURCE]", paragraph.text
        print "\t[EDITED]", text

        self.assertEqual(text, edited)

    ontology = Rewriter.ontology

if __name__ == '__main__':
    unittest.main()
