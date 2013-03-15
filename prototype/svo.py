#!/usr/bin/python
# -*- coding: utf-8 -*-
from estructura import *
from conf import *
from global_operator import *
import logging, unidecode

logger    = logging.getLogger('svo')
handler   = logging.FileHandler('logs/svo.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler) 
logger.setLevel(logging.INFO)

class SVOelement(object):
    def __init__(self, estructura=None):
        self.estructura = estructura or get_estructura_vacia()
        self.words = self.estructura.words
        self.sentiment = None
        self.sentence_id = None

    def asignar_sentimiento(self):
        # -------- (caso especial, por Freeling)
        # El horrible gato con hermosas botas violó a Alicia.
        # El horrible gato (0,75) + (0,50) = (0,125)
        # hermosas botas (60,0)
        # Alicia (0,0)
        # -------- (caso general)
        # La magnánima Justicia (de las abyectas acciones) (30,0) + (0,50)= (30,50)
        # las abyectas acciones (0,40)
        # mi vida (0,0)
        # --------
        # El magnánimo juez condenó al abyecto ladrón por robar un banco usurero
        # El magnánimo juez 30,0
        # el abyecto ladrón  0,40 + 0,35
        # robar un banco usurero 0,50
        # un banco usurero 0,40
        # --------
        for word in self.words:
            if word.lemma.endswith('mente'):
                w = word.lemma[:-5]
            else:
                w = word.lemma
            if subjetivemas.has_key(w):  # and not(scripts_verbales.has_key(w))
                word.sentiment = subjetivemas[w]
                self.add_sentiment(word.sentiment)
        
    def add_sentiment(self, (pos, neg)):
        self.sentiment = (self.sentiment[0] + pos, self.sentiment[1] + neg)

    def add_inverted_sentiment(self, (pos, neg)):
        self.sentiment = (self.sentiment[0] + neg, self.sentiment[1] + pos)

    def get_sentiment(self):
        if not(self.sentiment):
            self.sentiment = (0,0)
            self.asignar_sentimiento()
        return self.sentiment

    def __str__(self):
        return self.estructura.__str__()

class ModalVerb(object):
    def __init__(self, verb):
        self.verb = verb
        self.value = (0, 0)
        if subjetivemas.has_key(self.verb.lemma): self.value = subjetivemas[self.verb.lemma]
        logger.info("ModalVerb: %s (%d, %d)" % (self.verb.lemma, self.value[0], self.value[1]))

    def __str__(self):
        return self.verb.lemma.__str__()

class Verb(object):
    def __init__(self, verb, marco_verbal):
        self.verb = verb
        self.marco_verbal = marco_verbal
        
    def __str__(self):
        return self.verb.words[0].lemma.__str__()

class SVO(object):
    def __init__(self):
        self.subject = None
        self.modal_verb = None
        self.verb = None
        self.object = None
        self.others = []
        self.adverbs = []
        self.privativa = []
        self.global_operator = None
        self.sentiments = ((0,0), (0,0), (0,0))

    def build(self):
        self.subject = self.subject or SVOelement(get_estructura_vacia())
        self.modal_verb = self.modal_verb or ModalVerb(Palabra(''))
        self.verb = self.verb or Verb(get_estructura_vacia()) 
        self.object = self.object or SVOelement(get_estructura_vacia())
        self.others = self.others or [SVOelement(get_estructura_vacia())]
        self.adverbs = self.adverbs or [SVOelement(get_estructura_vacia())]
        self.privativa = self.privativa or [SVOelement(get_estructura_vacia())]
        self.global_operator = self.global_operator or GlobalOperator(('x', None, 0))

    def asignar_sentimiento_nominal(self):
        # obtener sentiment nominal de c/u: S, O, X
        subject_sentimiento_nominal = self.subject.get_sentiment()
        object_sentimiento_nominal = self.object.get_sentiment()

    def asignar_sentimiento_verbal(self):

        # incluir acá valor que viene de modal
        pos_mod, neg_mod = self.modal_verb.value

        # (G)lobally-operating verb
        if self.global_operator.category:
            if self.global_operator.category == 'G':
                # logger.info("global_operator: %s" % self.global_operator)
                self.subject.add_sentiment((0, self.global_operator.value))
                self.object.add_sentiment((0, self.global_operator.value))
                return
            elif self.global_operator.category == 'N':
                return
            elif self.global_operator.category == '_':
                return

        # marco_verbal: (A)gentivo, (O)bjetivo, (D)osAguas, (E)cuativo, (S)witch, (N)eutro
        if subjetivemas.has_key(self.verb.verb.words[0].lemma):
            pos, neg = subjetivemas[self.verb.verb.words[0].lemma]
        else:
            pos, neg = (1.0, 1.0)

        if self.verb.marco_verbal == 'A':
            self.subject.add_sentiment((pos, neg+neg_mod))

        elif self.verb.marco_verbal == 'O':
            self.object.add_sentiment((pos, neg+neg_mod))

        elif self.verb.marco_verbal == 'D':
            self.subject.add_sentiment((pos, neg+neg_mod))
            self.object.add_sentiment((pos, neg+neg_mod))

        elif self.verb.marco_verbal == 'E':
            subject_sentiment = self.subject.get_sentiment()
            object_sentiment  = self.object.get_sentiment()
            others_sentiment  = reduce(lambda (a,b), (c,d): (a+c, b+d), [o.get_sentiment() for o in self.others], (0,0))
            self.subject.add_sentiment((object_sentiment))
            self.subject.add_sentiment((others_sentiment))
            self.object.add_sentiment((subject_sentiment))
            map(lambda o: o.add_sentiment((subject_sentiment)), self.others)

        elif self.verb.marco_verbal == 'S':
            self.subject.add_sentiment((pos, neg+neg_mod))
            self.object.add_inverted_sentiment((pos, neg+neg_mod))

        elif self.verb.marco_verbal == 'N':
            pass

    def asignar_sentimiento_adverbial(self):
        # sentiment adverbial se agrega a S
        pos, neg = reduce(lambda (a,b), (c,d): (a+c, b+d), [adv.get_sentiment() for adv in self.adverbs], (0,0))
        self.subject.add_sentiment((pos, neg))

    def asignar_sentimiento_privativa(self):
        posicion_verbo = self.verb.verb.words[0].position
        for eprivativa in self.privativa:
            posicion_eprivativa = eprivativa.words[0].position
            pos_eprivativa, neg_eprivativa = eprivativa.get_sentiment()
            if posicion_eprivativa < posicion_verbo and self.subject:
                self.subject.add_inverted_sentiment((pos_eprivativa, neg_eprivativa))
            elif posicion_eprivativa > posicion_verbo:
                if self.object:
                    self.object.add_inverted_sentiment((pos_eprivativa, neg_eprivativa))
                else:
                    for other in self.others:
                        other.add_inverted_sentiment((pos_eprivativa, neg_eprivativa))

    def asignar_sentimiento(self):
        self.asignar_sentimiento_nominal()
        self.asignar_sentimiento_verbal()
        self.asignar_sentimiento_adverbial()
        self.asignar_sentimiento_privativa()

    def __str__(self):
        suma_others = reduce(lambda (a,b), (c,d): (a+c, b+d), [o.get_sentiment() for o in self.others])
        cada_other = ' '.join(["(%d, %d)" % s for s in [o.get_sentiment() for o in self.others]])
        # cada_entidad_privativa = ' '.join(["%s" % es.__str__() for es in self.privativa])
        output = "S[%s] (%s) MV[%s] V[%s](%s)  O[%s] (%s)  X[%s] (%s <-- {%s})  <A[%s] (%s)> <GO[%s]> <Eprivativa[%s]>" % (
            self.subject.__str__(), "%d, %d" % self.subject.get_sentiment(),
            self.modal_verb.__str__(),
            self.verb.__str__(), self.verb.marco_verbal,
            self.object.__str__() or u'x',
            "%d, %d" % self.object.get_sentiment(),
            '|'.join([o.__str__() for o in self.others]),
            "%d, %d" % suma_others,
            cada_other,
            '|'.join([a.__str__() for a in self.adverbs]),
            "%d, %d" % reduce(lambda (a,b), (c,d): (a+c, b+d), [adv.get_sentiment() for adv in self.adverbs]),
            self.global_operator.__str__(),
            "x", # cada_entidad_privativa,
        )
        return unidecode.unidecode(output)