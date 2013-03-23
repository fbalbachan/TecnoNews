#!/usr/bin/env python
#-*- coding: utf-8 -*-
import re, sys, json
from msi_data import *

def tag2msi(tag):
    category = tag[0]
    result = {"category": word_category[category], "person": 3}
    attributes = attribute_map[category]                                
                                                                    
    # special case ('N' has a two-letter attribute)
    if category == 'N':                                             
        for (position, letter) in zip([1,2,3,45,6], [tag[1], tag[2], tag[3], tag[4:6], tag[6]]):          
            attribute, values = attributes[position]                    
            result[attribute] = values[letter]                                                        
    else:                                                               
        for (position, letter) in enumerate(tag[1:], 1):                
            attribute, values = attributes[position]                # ("function", {"0": None, "P": u"participio"})
            result[attribute] = values[letter]                      # result["function"] = values["P"]
    
    return result

if __name__ == '__main__':
    try: print(tag2msi(sys.argv[1]))
    except IndexError: print "please provide a tag, e.g.: ./msi_mapper.py AQ0MS0"
