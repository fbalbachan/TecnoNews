#!/usr/bin/python
# -*- coding: utf-8 -*-
import codecs
from model.sentence import *
from utils.logger_utils import *

logger = get_logger('entinews')

def parse_sentence(input_sentence):
    """ text -> Sentence """
    logger.info(u"\n%s\ninput sentence: %s" % ("*"*80, input_sentence))
    sentence = Sentence(input_sentence)
    return sentence

def extract_entities(sentence):
    """ Sentence -> [Structure, Structure, ...] """
    logger.info(u"\n%s\nsentence: %s" % ("*"*80, sentence))
    entities = sentence.entities
    for i, entity in enumerate(entities, 1): logger.info(u"%d) entity: %s | head: %s | head msi: %s" % (i, entity, entity.head, entity.msi))
    return entities

def extract_subject(sentence):
    """ Sentence -> Structure """
    logger.info(u"\n%s\nsentence: %s" % ("*"*80, sentence))
    subject = sentence.subject
    logger.info(u"subject: %s | %s" % (subject, subject.msi))
    return subject
    

if __name__ == '__main__':
    from utils.formatter import *

    if len(sys.argv) > 0:
        input_text = sys.argv[1]
    else:
        input_text = codecs.open('input/sentence.txt', 'r', 'utf-8').read().strip()

    sentence = parse_sentence(input_text)

    entities = extract_entities(sentence)
    print logged_entities(entities)

    subject = extract_subject(sentence)
    print logged_subject(subject)
