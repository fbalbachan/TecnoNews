# -*- coding: utf-8 -*-

import unicodedata

def remove_accents(input_str):
    nkfd_form = unicodedata.normalize('NFKD', unicode(input_str))
    return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])

def set_first_letter_case(source, destination):
    if source[0].upper() == source[0]:
        destination = destination[0].upper() + destination[1:]
    return destination