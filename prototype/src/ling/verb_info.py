# -*- coding: utf-8 -*-
import ConfigParser

from src.sentiment.verbalScript import VerbalScript
from src.utils.csvwrapper import unicode_csv_reader
from src.utils.configProvider import ConfigProvider


allowed_boxes_according_to_verb_transitivity = {
    # verb_category : available_boxes
    'TRANSITIVE'   : [ 'verb', 'subject', 'od', 'oi', 'instrument_goal', 'adjuncts' ],
    'INTRANSITIVE' : ['verb', 'subject', 'oi', 'instrument_goal', 'adjuncts' ],
    'REGIMEN'      : ['verb', 'subject', 'regimen', 'instrument_goal', 'adjuncts' ],
    'EQUATIVE'     : ['verb', 'subject', 'oi', 'equative', 'instrument_goal', 'adjuncts' ],
    'EXISTENTIAL'  : ['verb', 'od', 'instrument_goal', 'adjuncts' ],
    'IMPERSONAL'   : ['verb', 'instrument_goal', 'adjuncts' ],
}

allowed_boxes_for_passive_verbs = [ 'verb', 'subject', 'od', 'instrument_goal', 'adjuncts' ]

allowed_boxes_for_unimember_sentences = [ 'instrument_goal', 'subject', 'adjuncts' ]

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

def get_sentimental_script_of(lemma):
    try:
        return verbs[lemma.lower()]['script']
    except KeyError:
        return VerbalScript(lemma)

def get_transitivity(verb):
    try:
        return verbs[verb.lower()]['transitivity']
    except KeyError:
        return transitivities["I"]

def allowed_boxes(transitivity):
    try:
        result = allowed_boxes_according_to_verb_transitivity[transitivity]
    except KeyError:
        result = None
    return result

# load verb resources from file
Config = ConfigProvider()

verb_file =  Config.get("resources", "verbal_scripts")
verb_file_reader = unicode_csv_reader(open(verb_file, 'r'), first_line_is_header = False, delimiter=',')
verbs = {}

for lemma, script_klass, transitivity, agentive_coef, objective_coef in verb_file_reader:
    coefs = []
    for coef in [agentive_coef, objective_coef]:
        coef = coef.strip()
        if not coef: coef = "0"
        coefs.append(float(coef) / 100)

    verbs[lemma]                 = {}
    verbs[lemma]['script']       = VerbalScript(lemma, scripts[script_klass], coefs[0], coefs[1])
    verbs[lemma]['transitivity'] = transitivities[transitivity]
    verbs[lemma]['boxes']        = allowed_boxes_according_to_verb_transitivity[transitivities[transitivity]]
