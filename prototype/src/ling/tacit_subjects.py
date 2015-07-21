#!/usr/bin/python
# -*- coding: utf-8 -*-
from src.model.entity.tacitEntity import TacitEntity
from src.model.entity.animityEnum import AnimityEnum
from src.ling.numberEnum import NumberEnum
from src.ling.genderEnum import GenderEnum

tacit_subjects = {(0, NumberEnum.singular, GenderEnum.neutral): None,
                  (1, NumberEnum.singular, GenderEnum.neutral): 'yo',
                  (2, NumberEnum.singular, GenderEnum.neutral): 'tú',

                  (3, NumberEnum.invariable, GenderEnum.neutral):   'lo',
                  (3, NumberEnum.singular,   GenderEnum.neutral):   'él/ella',
                  (3, NumberEnum.singular,   GenderEnum.masculine): 'él',
                  (3, NumberEnum.singular,   GenderEnum.feminine):  'ella',

                  (1, NumberEnum.plural, GenderEnum.neutral):   'nosotros/nosotras',
                  (1, NumberEnum.plural, GenderEnum.masculine): 'nosotros',
                  (1, NumberEnum.plural, GenderEnum.feminine):  'nosotras',

                  (2, NumberEnum.plural, GenderEnum.neutral):   'ustedes',

                  (3, NumberEnum.plural, GenderEnum.neutral):   'ellos/ellas',
                  (3, NumberEnum.plural, GenderEnum.masculine): 'ellos',
                  (3, NumberEnum.plural, GenderEnum.feminine):  'ellas', }


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
    return TacitEntity("alguien", {"category": "pronoun", "number": NumberEnum.invariable, "gender": GenderEnum.neutral,
                                   "person": 3, "type": "indefinite", "case": None, "animity": AnimityEnum.animated,
                                   "semantic_classification": None})


def something():
    return TacitEntity("algo", {"category": "pronoun", "number": NumberEnum.invariable, "gender": GenderEnum.neutral,
                                "person": 3, "type": "indefinite", "case": None, "animity": AnimityEnum.inanimate,
                                "semantic_classification": None})


def this():
    return TacitEntity("esto", {"category": "pronoun", "number": NumberEnum.singular, "gender": GenderEnum.neutral,
                                "person": 3, "type": "demonstrative", "case": None, "animity": AnimityEnum.inanimate,
                                "semantic_classification": None})


def impersonal(entity):
    entity.attributes = {"tacit": None, "impersonal": None}
    entity.msi["number"] = NumberEnum.invariable
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
    tacit_subject = tacit_subjects[(verb.msi['person'],
                                    verb.msi['number'],
                                    (verb.msi['gender'] or GenderEnum.neutral)
                                    )]
    return tacit_subject
