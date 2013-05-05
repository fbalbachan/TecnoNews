#!/usr/bin/python
# -*- coding: utf-8 -*-
import codecs
from model.sentence import *
from utils.logger_utils import *

logger = get_logger('entinews')

def parse_sentence(input_sentence):
    """ text -> Sentence """
    sentence = Sentence(input_sentence)
    # logger.info("\n%s\nsentence: %s" % ("*"*80, sentence.input_sentence))
    return sentence

def extract_entities(sentence):
    """ Sentence -> [Structure, Structure, ...] """
    # logger.info("\n%s\nsentence: %s" % ("*"*80, sentence.input_sentence))
    entities = sentence.entities
    # for i, entity in enumerate(entities, 1): logger.info("%d) entity: %s | head: %s | head msi: %s" % (i, entity, entity.head, entity.msi))
    return entities

def extract_subject(sentence):
    """ Sentence -> Structure """
    # logger.info("\n%s\nsentence: %s" % ("*"*80, sentence.input_sentence))
    subject = sentence.subject
    # logger.info("subject: %s | %s" % (subject, subject.msi))
    return subject

#     if len(sys.argv) > 1:
#         input_text = sys.argv[1]
#     else:
#         input_text = codecs.open('input/sentence.txt', 'r', 'utf-8').read().strip()

if __name__ == '__main__':

    while True:
        input_text = raw_input('> ').decode('utf-8')
        if input_text == 'q': exit()

        sentence = parse_sentence(input_text)

        entities = extract_entities(sentence)
        for entity in entities:
            print "\nentity: ", entity
            print "   msi: ", entity.msi

        subject = extract_subject(sentence)
        print "\nsubject: ", subject
        print "    msi: ", subject.msi

        verb = sentence.verb
        print "\nverb: ", sentence.verb
        print "\t transitivity: ", sentence.verb_transitivity
        print "\t script: ", sentence.verb_script_class

        print "\nallowed boxes: ", sentence.boxes

        print