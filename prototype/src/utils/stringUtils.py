# -*- coding: utf-8 -*-

import sys
import unicodedata


def remove_accents(input_str):
    nkfd_form = unicodedata.normalize('NFKD', unicode(input_str))
    return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])


def set_first_letter_case(source, destination):
    if source[0].upper() == source[0]:
        destination = destination[0].upper() + destination[1:]
    return destination


def has_type_encoding(obj, obj_type=str, encoding='UTF-8'):

    if sys.version_info >= (3,0,0):
        # for Python 3
        if isinstance(obj, bytes):
            s = obj.decode('ascii')  # or  obj = str(obj)[2:-1]

    else:
        # for Python 2
        if type(obj) is obj_type:

            if obj_type is unicode:
                return True

            if obj_type is str:
                try:
                    obj.decode(encoding)
                    return True

                except Exception as e:
                    return False

            else:
                return False

        else:
            return False