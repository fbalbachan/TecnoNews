#!/usr/bin/python
# -*- coding: utf-8 -*-
from src.model.entity.tacitEntity import TacitEntity
from src.model.entity.animity import Animity
from src.ling.number import Number
from src.ling.gender import Gender

tacit_subjects = {(0,   Number.singular, Gender.neutral):    None,
                  (1,   Number.singular, Gender.neutral):    'yo',
                  (2,   Number.singular, Gender.neutral):    'tú',

                # (3,   Number.invariable, Gender.neutral):  'lo',
                  (3,   Number.singular,  Gender.neutral):   'él/ella',
                  (3,   Number.singular, Gender.masculine):  'él',
                  (3,   Number.singular, Gender.feminine):   'ella',

                  (1,   Number.plural,   Gender.neutral):    'nosotros/nosotras',
                  (1,   Number.plural,   Gender.masculine):  'nosotros',
                  (1,   Number.plural,   Gender.feminine):   'nosotras',

                  (2,   Number.plural,   Gender.neutral):    'ustedes',
                  (2,   Number.plural,   Gender.masculine):  'vosotros',
                  (2,   Number.plural,   Gender.feminine):   'vosotras',

                  (3,   Number.plural,   Gender.neutral):    'ellos/ellas',
                  (3,   Number.plural,   Gender.masculine):  'ellos',
                  (3,   Number.plural,   Gender.feminine):   'ellas', }


def get_entity_some(animity, is_implicit=False, is_impersonal=False):
    if animity == Animity.animated:
        entity = somebody()
    elif animity == Animity.inanimate:
        entity = something()
    else:  # Animity.bianimate:
        entity = bianimate_something()

    if is_implicit:
        entity = implicit(entity)
    elif is_impersonal and animity == Animity.animated:
        entity = impersonal(entity)

    return entity


def bianimate_something():
    entity = something()
    entity.msi["animity"] = Animity.bianimate
    return entity


def impersonal_somebody():
    return impersonal(somebody())


def somebody():
    return TacitEntity("alguien", {"category": "pronoun", "number": Number.invariable, "gender": Gender.neutral,
                                   "person": 3, "type": "indefinite", "case": None, "animity": Animity.animated,
                                   "semantic_classification": None})


def something():
    return TacitEntity("algo", {"category": "pronoun", "number": Number.invariable, "gender": Gender.neutral,
                                "person": 3, "type": "indefinite", "case": None, "animity": Animity.inanimate,
                                "semantic_classification": None})


def this():
    return TacitEntity("esto", {"category": "pronoun", "number": Number.singular, "gender": Gender.neutral,
                                "person": 3, "type": "demonstrative", "case": None, "animity": Animity.inanimate,
                                "semantic_classification": None})


def impersonal(entity):
    entity.attributes = {"tacit": None, "impersonal": None}
    entity.msi["number"] = Number.invariable
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
    tacit_subject = tacit_subjects[(verb.person(),
                                    verb.number(),
                                    (verb.gender() or Gender.neutral))]
    return tacit_subject
