#!/usr/bin/python
# -*- coding: utf-8 -*-
import codecs
from sentence import *
from utils.logger_utils import *

def extract_entities(input_sentence):
    logger = get_logger('sentilecto')
    logger.info(u"input sentence: %s" % input_sentence)

    analyzer = FreelingAnalyzer()
    sentence = Sentence(input_sentence, analyzer)

    entities = sentence.get_entities() # TODO entidades_a_izquierda, entidades_a_derecha = sentence.get_entities()
    logger.info(u"entities: %s" % [e for e in entities])
    return entities                    # TODO return (entidades_a_izquierda, entidades_a_derecha)


if __name__ == '__main__':
    sentence = codecs.open('sentence.txt', 'r', 'utf-8').read().strip()

    entities = extract_entities(sentence)

    for entity in entities:
        print entity, entity.head()