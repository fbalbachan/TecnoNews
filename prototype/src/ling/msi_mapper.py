#!/usr/bin/env python
#-*- coding: utf-8 -*-
import re, sys, json
from msi_data import *

default_msi = {"person": 3, "number": u"singular", "gender": u"neutral"}
empty_msi = {"person": None, "number": None, "gender": None}

def tag2fullmsi(tag):
    category = tag[0]
    result = {"category": word_category[category]}
    attributes = attribute_map[category]                                
                                                                    
    # special case ('N' has a two-letter attribute)
    if category == 'N':                                             
        for (position, letter) in zip([1,2,3,45,6], [tag[1], tag[2], tag[3], tag[4:6], tag[6]]):          
            attribute, values = attributes[position]                    
            result[attribute] = values[letter]                                                        
    else:                                                               
        for (position, letter) in enumerate(tag[1:], 1):                
            attribute, values = attributes[position]     # ("function", {"0": None, "P": u"participio"})
            result[attribute] = values[letter]           # result["function"] = values["P"]
    
    return result

def msi(a_msi):

    try:
        if a_msi["gender"]:
            gender = a_msi["gender"]
        else:
            gender = u"neutral"
    except KeyError:
        gender = u"neutral"

    try:
        if a_msi["number"]:
            number = a_msi["number"]
        else:
            number = u"singular"
    except KeyError:
        number = u"singular"

    try:
        if a_msi["person"]:
            person = a_msi["person"]
        else:
            person = 3
    except KeyError:
        person = 3

    result = {"person": person, "gender": gender, "number": number}
    return result


if __name__ == '__main__':
    try:
        print(tag2fullmsi(sys.argv[1]))
        print(msi(tag2fullmsi(sys.argv[1])))
    except IndexError: print "please provide a tag, e.g.: ./msi_mapper.py AQ0MS0"
