# -*- coding: utf-8 -*-
__author__ = 'Martin Caramés Abente'

# Python 2 ran with the 'enum' 0.4.4 package, where these members were plain strings: StrEnum keeps
# them comparable to strings, JSON serializable and printable as their value
from enum import StrEnum


class Number(StrEnum):
    singular = "singular"
    plural = "plural"
    invariable = "invariable"

    @classmethod
    def most_specific(cls, number1, number2):
        if number1 is cls.singular and number2 is cls.singular:
            return cls.singular

        elif number1 is cls.singular and number2 is cls.invariable \
                or number1 is cls.invariable and number2 is cls.singular:
            return cls.singular

        elif number1 is cls.plural and number2 is cls.plural:
            return cls.plural

        elif number1 is cls.plural and number2 is cls.invariable \
                or number1 is cls.invariable and number2 is cls.plural:
            return cls.plural

        else:
            return None

    @classmethod
    def numbers_match(cls, number1, number2):
        match = number1 in [number2, cls.invariable] \
                or number2 in [cls.invariable]
        return match
