#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import itertools
from conf import *
from estructura import *
from palabra import *
from oracion import *
from texto import *
from est import *
from sentiment import *
from utils.tokenize import sentence_delimiters

logger    = logging.getLogger('sentitext')
handler   = logging.FileHandler('logs/sentitext.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

def extract_entities(input_sentence):
    logger.info("input sentence: %d) '%s'" % (i, input_sentence))
    entities = []
    sentence = Sentence(input_sentence)
    entidades_a_izquierda, entidades_a_derecha = sentence.hallar_entidades()
    return (entidades_a_izquierda, entidades_a_derecha)

def format_entities(entities):
    entidades_ordenadas = sorted(entities, key=lambda e: e.estructura.__str__())
    logger.info('.'*80); logger.info("entidades (candidatos): %s" % ' - '.join([e.__str__() for e in entidades_ordenadas]))

    entities_final = []
    groups = itertools.groupby(entidades_ordenadas, lambda e: e.estructura.sin_determinantes().__str__())
    for (representacion, lista_de_entidades) in groups:
        others = list(lista_de_entidades)
        if len(others) > 1:
            original = others[0]
            entities_final.append(original)
            for other_entity in others[1:]:
                if other_entity.sentence_id - original.sentence_id <= 3:
                    original.add_sentiment(other_entity.get_sentiment())
                else:
                    entities_final.append(other_entity)
        else:
            entities_final.append(others[0])

    return entities_final


if __name__ == '__main__':
    sentence = codecs.open('sentence.txt', 'r', 'utf-8').read()

    entities = extract_entities(sentence)

    # for svo in svos: print u"%s" % svo

    # for e in entities_with_sentiment:
    #     print u"%s (sentence id: %d) -> %s" % (e, e.sentence_id, e.get_sentiment())

