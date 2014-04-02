#!/usr/bin/python
# -*- coding: utf-8 -*-
import ConfigParser
from utils.logger_utils import *
from utils.csvwrapper import *
import codecs

# logger = get_logger('entinews')

allowed_boxes_according_to_verb_transitivity = {
    # verb_category : available_boxes
    'TRANSITIVE'   : {'verb': True, 'subject': True, 'od': True, 'oi': True, 'regimen': False, 'equative': False, 'adjuncts': True},
    'INTRANSITIVE' : {'verb': True, 'subject': True, 'od': False, 'oi': True, 'regimen': False, 'equative': False, 'adjuncts': True},
    'REGIMEN'      : {'verb': True, 'subject': True, 'od': False, 'oi': False, 'regimen': True, 'equative': False, 'adjuncts': True},
    'EQUATIVE'     : {'verb': True, 'subject': True, 'od': False, 'oi': True, 'regimen': False, 'equative': True, 'adjuncts': True},
    'EXISTENTIAL'  : {'verb': True, 'subject': False, 'od': True, 'oi': False, 'regimen': False, 'equative': False, 'adjuncts': True},
    'IMPERSONAL'   : {'verb': True, 'subject': False, 'od': False, 'oi': False, 'regimen': False, 'equative': False, 'adjuncts': True},
}

allowed_boxes_for_passive_verbs = {'verb': True, 'subject': True, 'od': True, 'oi': False, 'regimen': False, 'equative': False, 'adjuncts': True}

allowed_boxes_for_unimember_sentences = {'verb': False, 'subject': True, 'od': False, 'oi': False, 'regimen': False, 'equative': False, 'adjuncts': True}

transitivities = {
    'T': 'TRANSITIVE',
    'I': 'INTRANSITIVE',
    'R': 'REGIMEN',
    'E': 'EQUATIVE',
    'X': 'INTRANSITIVE',
    'H': 'EXISTENTIAL',
    'M': 'IMPERSONAL',
}

scripts = {
    'A': 'AGENTIVE',
    'E': 'EQUATIVE',
    'D': 'DOSAGUAS',
    'O': 'OBJECTIVE',
    'N': 'NEUTRAL',
    'S': 'SWITCH',
}

def get_script_class(verb):
    try:
        return verbs[verb.lower()]['script']
    except KeyError:
        # logger.warn("wrong/missing verb info: ", verb)
        return None

def get_transitivity(verb):
    try:
        return verbs[verb.lower()]['transitivity']
    except KeyError:
        # logger.warn("wrong/missing verb info: ", verb)
        return None

def allowed_boxes(verb_transitivity):
    try:
        result = allowed_boxes_according_to_verb_transitivity[verb_transitivity]
    except KeyError:
        # logger.error("wrong/missing verb transitivity: ", verb_transitivity)
        result = None
    return result

# load verb resources from file
Config = ConfigParser.ConfigParser()
Config.read("config")

verb_file =  Config.get("resources", "verbal_scripts")
verb_file_reader = unicode_csv_reader(codecs.open(verb_file, 'r', 'utf-8'), first_line_is_header=False, delimiter=',')
verbs = {}
for line in verb_file_reader:
    verb_word, verb_script, verb_transitivity = line[0], line[1], line[2]
    verbs[verb_word]                 = {}
    verbs[verb_word]['script']       = scripts[verb_script]
    verbs[verb_word]['transitivity'] = transitivities[verb_transitivity]
    verbs[verb_word]['boxes']        = allowed_boxes_according_to_verb_transitivity[transitivities[verb_transitivity]]
