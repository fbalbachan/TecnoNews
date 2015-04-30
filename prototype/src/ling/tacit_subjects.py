#!/usr/bin/python
# -*- coding: utf-8 -*-
from src.model.entity.tacitEntity import TacitEntity
from src.model.entity.animityEnum import AnimityEnum
from src.ling.numberEnum import NumberEnum

tacit_subjects = {(0, 'singular', 'neutral'): None,
                  (1, 'singular', 'neutral'): 'yo',
                  (2, 'singular', 'neutral'): 'tú',

                  (3, 'invariable', 'neutral'): 'lo',
                  (3, 'singular', 'neutral')  : 'él/ella',
                  (3, 'singular', 'masculine'): 'él',
                  (3, 'singular', 'feminine') : 'ella',

                  (1, 'plural', 'neutral')  : 'nosotros/nosotras',
                  (1, 'plural', 'masculine'): 'nosotros',
                  (1, 'plural', 'feminine') : 'nosotras',

                  (2, 'plural', 'neutral')  : 'ustedes',

                  (3, 'plural', 'neutral')  : 'ellos/ellas',
                  (3, 'plural', 'masculine'): 'ellos',
                  (3, 'plural', 'feminine') : 'ellas',}


def get_entity_some(animity, is_implicit=False, is_impersonal=False):
    if animity == AnimityEnum.animated:
        entity = somebody()
    elif animity == AnimityEnum.inanimate:
        entity = something()
    else:  # AnimityEnum.bianimate:
        entity = bianimate_something()

    if is_implicit:
        entity = implicit(entity)
    elif is_impersonal and animity == AnimityEnum.animated:
        entity = impersonal(entity)

    return entity


def bianimate_something():
    entity = something()
    entity.msi["animity"] = AnimityEnum.bianimate
    return entity


def impersonal_somebody():
    return impersonal(somebody())


def somebody():
    return TacitEntity("alguien", {"category": "pronoun", "number": "invariable", "gender": "neutral",
                                   "person": 3, "type": "indefinite", "case": None, "animity": AnimityEnum.animated,
                                   "semantic_classification": None})


def something():
    return TacitEntity("algo", {"category": "pronoun", "number": "invariable", "gender": "neutral",
                                "person": 3, "type": "indefinite", "case": None, "animity": AnimityEnum.inanimate,
                                "semantic_classification": None})


def this():
    return TacitEntity("esto", {"category": "pronoun", "number": "singular", "gender": "neutral",
                                "person": 3, "type": "demonstrative", "case": None, "animity": AnimityEnum.inanimate,
                                "semantic_classification": None})


def impersonal(entity):
    entity.attributes = {"tacit": None, "impersonal": None}
    entity.msi["number"] = NumberEnum.impersonal_invariable
    return entity


def implicit(entity):
    entity.attributes = {"tacit": None, "implicit": None}
    return entity


def implicit_somebody():
    return implicit(somebody())


def implicit_something():
    return implicit(something())


def implicit_bianimate_something():
    return implicit(bianimate_something())


def tacit_subject_for(verb):
    gender = verb.msi['gender'] if verb.msi['gender'] else "neutral"
    tacit_subject = tacit_subjects[(verb.msi['person'], verb.msi['number'], gender)]
    return tacit_subject