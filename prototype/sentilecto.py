#!/usr/bin/python
# -*- coding: utf-8 -*-
import codecs
from sentence import *
from logger_utils import *

def extract_entities(input_sentence):
    logger = get_logger('sentilecto')
    logger.info(u"input sentence: '%s'" % input_sentence)

    entities = []

    analyzer = FreelingAnalyzer()
    sentence = Sentence(input_sentence, analyzer)

    entities = sentence.get_entities() # TODO entidades_a_izquierda, entidades_a_derecha = sentence.get_entities()
    return entities                    # TODO return (entidades_a_izquierda, entidades_a_derecha)


if __name__ == '__main__':
    sentence = codecs.open('sentence.txt', 'r', 'utf-8').read()
    entities = extract_entities(sentence)
