#!/usr/bin/python
# -*- coding: utf-8 -*-
import codecs
from model.sentence import *
from utils.logger_utils import *

def parse_sentence(input_sentence):
    """ text -> Sentence """
    logger = get_logger('entinews')
    logger.info(u"\n%s\ninput sentence: %s" % ("*"*80, input_sentence))
    sentence = Sentence(input_sentence)
    
    return sentence

def extract_entities(sentence):
    """ Sentence -> [Structure, Structure, ...] """
    logger = get_logger('entinews')
    logger.info(u"\n%s\nsentence: %s" % ("*"*80, sentence))

    entities = sentence.entities
    for i, entity in enumerate(entities, 1): logger.info(u"%d) entity: %s | head: %s | head msi: %s" % (i, entity, entity.head, entity.msi))

    return entities


if __name__ == '__main__':
    sentence = codecs.open('input/sentence.txt', 'r', 'utf-8').read().strip()
    entities = extract_entities(sentence)
