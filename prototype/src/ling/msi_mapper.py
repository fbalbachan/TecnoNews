# -*- coding: utf-8 -*-
from src.ling.msi_data import *
from src.ling.gender import Gender
from src.ling.number import Number
import sys

default_msi = {"person": 3, "number": Number.singular, "gender": Gender.neutral}

empty_msi = {"person": None, "number": None, "gender": None}

def tag_to_full_msi(tag):
    category = tag[0]
    result = {"category": word_category[category]}
    attributes = attribute_map[category]

    # special case ('N' has a two-letter attribute)
    if category == 'N':
        for (position, letter) in zip([1,2,3,45,6], [tag[1], tag[2], tag[3], tag[4:6], tag[6]]):
            try:
                attribute, values = attributes[position]
                result[attribute] = values[letter]

            except KeyError:
                print("Unrecognized tag: ", tag, " - (position: ", position, ", letter: ", letter, ")")
                raise Exception()

    elif category == "F":
        result["type"] = attributes[tag[1:]]

    else:
        for (position, letter) in enumerate(tag[1:], 1):
            try:
                attribute, values = attributes[position]     # ("function", {"0": None, "P": u"participio"})
                result[attribute] = values[letter]           # result["function"] = values["P"]

            except KeyError:
                print("Unrecognized tag: ", tag, " - (position: ", position, ", letter: ", letter, ")")
                raise Exception

    return result

def msi(a_msi):

    try:
        gender = (a_msi["gender"] or default_msi["gender"])
    except KeyError:
        gender = default_msi["gender"]

    try:
        number = (a_msi["number"] or default_msi["number"])
    except KeyError:
        number = default_msi["number"]

    try:
        person = (a_msi["person"] or default_msi["person"])
    except KeyError:
        person = default_msi["person"]

    result = {"person": person, "gender": gender, "number": number}
    return result

def msi_concordance(subject, verb):
    """Structure -> boolean"""
    # print "msi_concordance", subject, subject.label, subject.position, subject.msi, verb, verb.position, verb.msi
    return (subject.person() == verb.person()) \
            and (subject.number() == verb.number())
