# -*- coding: utf-8 -*-
import ConfigParser

from src.sentiment.verbalScript import VerbalScript
from src.utils.csvwrapper import unicode_csv_reader
from src.model.entity.animity import Animity


transitivity_values = {'T': 'TRANSITIVE',
                       'I': 'INTRANSITIVE',
                       'R': 'REGIMEN',
                       'E': 'EQUATIVE',
                       'X': 'INTRANSITIVE',
                       'H': 'EXISTENTIAL',
                       'M': 'IMPERSONAL', }

allowed_boxes_according_to_verb_transitivity = \
    {  # verb_category : available_boxes
       'TRANSITIVE':    ['verb', 'subject', 'od', 'oi', 'instrument_goal', 'adjuncts'],
       'INTRANSITIVE':  ['verb', 'subject', 'oi', 'instrument_goal', 'adjuncts'],
       'REGIMEN':       ['verb', 'subject', 'regimen', 'instrument_goal', 'adjuncts'],
       'EQUATIVE':      ['verb', 'subject', 'oi', 'equative', 'instrument_goal', 'adjuncts'],
       'EXISTENTIAL':   ['verb', 'od', 'instrument_goal', 'adjuncts'],
       'IMPERSONAL':    ['verb', 'instrument_goal', 'adjuncts'], }

existing_boxes = set(sum([allowed_boxes_according_to_verb_transitivity[value]
                          for key, value in transitivity_values.iteritems()], []))

allowed_boxes_for_passive_verbs = ['verb', 'subject', 'od', 'instrument_goal', 'adjuncts']

allowed_boxes_for_minor_sentences = ['instrument_goal', 'subject', 'adjuncts']

animity_values = {'Anim': Animity.animated,
                  'Bi': Animity.bianimate,
                  'No': Animity.inanimate}

scripts = {'A': 'AGENTIVE',
           'E': 'EQUATIVE',
           'D': 'DOSAGUAS',
           'O': 'OBJECTIVE',
           'N': 'NEUTRAL',
           'S': 'SWITCH', }


def get_sentimental_script_of(verb_lemma):
    try:
        return verbs[verb_lemma.lower()]['script']
    except KeyError:
        return VerbalScript(verb_lemma)


def get_transitivity(verb):
    try:
        return verbs[verb.lower()]['transitivity']
    except KeyError:
        return transitivity_values["I"]


def allowed_boxes(transitivity):
    try:
        result = allowed_boxes_according_to_verb_transitivity[transitivity]
    except KeyError:
        result = None
    return result


def get_script_animity_for(verb_lemma, role_name):
    try:
        if role_name in ["od", "equative", "regimen"]:
            role_name = "oaf"

        verb_lemma = verb_lemma.lower()
        result = verbs[verb_lemma]['animity'][role_name]

    except KeyError:
        result = Animity.bianimate

    return result


def get_animity_value(animity_code):
    if animity_code in ['Anim', 'Bi', 'No']:
        return animity_values[animity_code]
    else:
        print "Wrong animity code in resource: ", animity_code
        return animity_values['Bi']


def get_transitivity_value(p_transitivity_code):
    if p_transitivity_code in ['T', 'I', 'R', 'E', 'X', 'H', 'M']:
        return transitivity_values[p_transitivity_code]
    else:
        print "Wrong transitivity code in resource: ", p_transitivity_code
        return transitivity_values['I']


# Load verb resources from file
Config = ConfigParser.ConfigParser()
Config.read("config")

verb_file = Config.get("resources", "verbal_scripts")
verb_file_reader = unicode_csv_reader(open(verb_file, 'r'), first_line_is_header=False, delimiter=',')
verbs = {}

for lemma, script_class, transitivity_code, agentive_coef, \
        objective_coef, subjAnimity_code, odAnimity_code in verb_file_reader:

    coefs = []
    for coef in [agentive_coef, objective_coef]:
        coef = coef.strip()
        if not coef:
            coef = "0"
        coefs.append(float(coef) / 100)

    verbs[lemma] = {}
    verbs[lemma]['script'] = VerbalScript(lemma, scripts[script_class], coefs[0], coefs[1])
    verbs[lemma]['transitivity'] = transitivity_values[transitivity_code]
    verbs[lemma]['boxes'] = allowed_boxes_according_to_verb_transitivity[transitivity_values[transitivity_code]]
    verbs[lemma]['animity'] = {'subject': get_animity_value(subjAnimity_code),
                               'oaf': get_animity_value(odAnimity_code)}