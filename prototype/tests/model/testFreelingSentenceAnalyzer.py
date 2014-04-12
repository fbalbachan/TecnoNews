#-*- coding: utf-8 -*-
from model.freelingSentenceAnalyzer import *
from model.sentence import *
import unittest


class FreelingSentenceAnalyzerTest(unittest.TestCase):

    def test(self):
        analyzer = FreelingSentenceAnalyzer()

        #sentence = Sentence("Leandro y Pepe dijo a Gustavo que el comer es saludable.")
        #sentence = Sentence("Dijo Leandro a Gustavo que el comer es saludable.")
        #sentence = Sentence("El hombre de la esquina rosada corrió.")
        #sentence = Sentence("Leandro comió la manzana que fue dejada.")
        #sentence = Sentence("Leandro comió la manzana que tiró y dejó.")

        #sentence = Sentence("El hombre de la esquina rosada comió al horrible Pedro y a José.") # No funciona en la version prod de Sentilecto
        #sentence = Sentence("Las manzanas comió Leandro.") # Esto no funciona en Sentilecto (queda en adjunto)
        #sentence = Sentence("Lo hizo para comer en su casa.") # Sujeto tácito
        #sentence = Sentence("Lo hizo para comer en su casa.") # Sujeto tácito
        sentence = Sentence("A Gustavo, Leandro le comió la manzana.")
        #sentence = Sentence("Él nos golpeó") # nos -> OD
        #sentence = Sentence("Me chocó de frente.") # me -> OI (licencia)
        #sentence = Sentence("Leandro desconfió de Gustavo.") # régimen

        #sentence = Sentence("El hombre de la esquina rosada le comió la manzana.")
        #sentence = Sentence("Pedro y Juan fueron comidos por Leandro.")

        #sentence = Sentence("El cartero todas las noches llegaba.")
        #sentence = Sentence("Muy bueno el libro que fue comprado.")

        #sentence = Sentence("Leandro comió y bebió agua.") # La "y" no es cláusula
        #sentence = Sentence("Fui aunque no tenía ganas.")

        #sentence = Sentence("Los charrúas comieron a Solís buscando satisfacer su hambre.")
        #sentence = Sentence("Todas las noches llegaba el cartero.")
        #sentence = Sentence("Toda la noche el cartero llegó con noticias.") # Tiene que concordar el MSI con el verbo
        #sentence = Sentence("Llegó el cartero toda la noche con noticias.") # Tiene que concordar el MSI con el verbo

        #sentence = Sentence("Odio comer en el horrible bar.")

        analyzer.analyze(sentence)


if __name__ == '__main__':
    unittest.main()
