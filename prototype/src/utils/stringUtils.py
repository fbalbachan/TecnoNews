# -*- coding: utf-8 -*-

import sys
import unicodedata


def remove_accents(input_str):
    nkfd_form = unicodedata.normalize('NFKD', str(input_str))
    return "".join([c for c in nkfd_form if not unicodedata.combining(c)])


def set_first_letter_case(source, destination):
    if source[0].upper() == source[0]:
        destination = destination[0].upper() + destination[1:]
    return destination


def has_type_encoding(obj, obj_type=str, encoding='UTF-8'):
    """True when obj is of obj_type; bytes count as text when they decode with the given encoding."""
    if isinstance(obj, bytes) and obj_type is str:
        try:
            obj.decode(encoding)
            return True
        except UnicodeDecodeError:
            return False
    return isinstance(obj, obj_type)