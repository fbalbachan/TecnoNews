#!/usr/bin/python
# -*- coding: utf-8 -*-
from utils.logger_utils import *
from utils.csvwrapper import *
import codecs

logger = get_logger('entinews')

required_boxes_according_to_verb_transitivity = {
    # verb_category : available_boxes
    'TRANSITIVE'   : {'od': True, 'oi': True, 'regimen': False, 'equative': False},
    'INTRANSITIVE' : {'od': False, 'oi': True, 'regimen': False, 'equative': False},
    'REGIMEN'      : {'od': False, 'oi': False, 'regimen': True, 'equative': False},
    'EQUATIVE'     : {'od': True, 'oi': True, 'regimen': False, 'equative': False},
    'UNKNOWN'      : {'od': False, 'oi': True, 'regimen': False, 'equative': False},
}

transitivities = {
    'T': 'TRANSITIVE',
    'I': 'INTRANSITIVE',
    'R': 'REGIMEN',
    'E': 'EQUATIVE',
    'X': 'UNKNOWN',
}

scripts = {
    'A': 'AGENTIVE',
    'E': 'EQUATIVE',
    'D': 'DOSAGUAS',
    'O': 'OBJECTIVE',
    'N': 'NEUTRAL',
    'S': 'SWITCH',
}

def verb_info(verb):
    try:
        return verbs[verb.lower()]
    except KeyError:
        logger.warn("wrong/missing verb info: ", verb)
        return {'script' : None, 'transitivity' : None}

def required_boxes(verb_transitivity):
    try:
        result = required_boxes_according_to_verb_transitivity[verb_transitivity]
    except KeyError:
        logger.error("wrong/missing verb transitivity: ", verb_transitivity)
        result = None
    return result

# load verb resources from file
verb_file = 'resources/scripts_verbales.csv'
verb_file_reader = unicode_csv_reader(codecs.open(verb_file, 'r', 'utf-8'), first_line_is_header=False, delimiter=',')
verbs = {}
for line in verb_file_reader:
    verb_word, verb_script, verb_transitivity = line[0], line[1], line[2]
    verbs[verb_word]                 = {}
    verbs[verb_word]['script']       = scripts[verb_script]
    verbs[verb_word]['transitivity'] = transitivities[verb_transitivity]
    verbs[verb_word]['boxes']        = required_boxes_according_to_verb_transitivity[transitivities[verb_transitivity]]