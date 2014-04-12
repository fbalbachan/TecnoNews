#!/usr/bin/python
# -*- coding: utf-8 -*-
import ConfigParser
import codecs

from src.utils.csvwrapper import *
from src.utils.logger_utils import *


# logger = get_logger('entinews')
allowed_boxes_according_to_verb_transitivity = {
    # verb_category : available_boxes
    'TRANSITIVE'   : [ 'verb', 'subject', 'od', 'oi', 'adjuncts' ],
    'INTRANSITIVE' : ['verb', 'subject', 'oi', 'adjuncts' ],
    'REGIMEN'      : ['verb', 'subject', 'regimen', 'adjuncts' ],
    'EQUATIVE'     : ['verb', 'subject', 'oi', 'equative', 'adjuncts' ],
    'EXISTENTIAL'  : ['verb', 'od', 'adjuncts' ],
    'IMPERSONAL'   : ['verb', 'adjuncts' ],
}

allowed_boxes_for_passive_verbs = [ 'verb', 'subject', 'od', 'adjuncts' ]

allowed_boxes_for_unimember_sentences = [ 'subject', 'adjuncts' ]

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
