#!/usr/bin/env python
#-*- coding: utf-8 -*-
import re, sys, json
from msi_data import *

default_msi = {"person": 3, "number": u"S", "gender": u"M"}

def tag2msi(tag):
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

def tag2filtered_msi(tag):
    msi = tag2msi(tag)

    try:
        if msi["gender"]:
            gender = msi["gender"]
        else:
            gender = u"M"
    except KeyError:
        gender = u"M"

    try:
        if msi["number"]:
            number = msi["number"]
        else:
            number = u"S"
    except KeyError:
        number = u"S"

    try:
        if msi["person"]:
            person = msi["person"]
        else:
            person = 3
    except KeyError:
        person = 3

    result = {"person": person, "gender": gender, "number": number}
    return result


if __name__ == '__main__':
    try:
        print(tag2msi(sys.argv[1]))
        print(tag2filtered_msi(sys.argv[1]))
    except IndexError: print "please provide a tag, e.g.: ./msi_mapper.py AQ0MS0"
