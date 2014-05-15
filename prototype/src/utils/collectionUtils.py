#-*- coding: utf-8 -*-

from itertools import groupby


def dict_by(objects, key_function):
    by_key = groupby(sorted(objects, key=key_function), key_function)
    by_key = { key: list(objects) for key, objects in by_key }
    return by_key