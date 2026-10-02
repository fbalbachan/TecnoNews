# -*- coding: utf-8 -*-
__author__ = 'Martin Caramés Abente'

# Python 2 ran with the 'enum' 0.4.4 package, where these members were plain strings: StrEnum keeps
# them comparable to strings, JSON serializable and printable as their value
from enum import StrEnum


class Gender(StrEnum):
    masculine = "masculine"
    feminine = "feminine"
    neutral = "neutral"

    @classmethod
    def most_specific(cls, gender1, gender2):
        if gender1 is cls.masculine and gender2 is cls.masculine:
            return cls.masculine

        elif gender1 is cls.masculine and gender2 is cls.neutral:
            return cls.masculine

        elif gender1 is cls.feminine and gender2 is cls.feminine:
           return cls.feminine

        elif gender1 is cls.feminine and gender2 is cls.neutral:
            return cls.feminine

        elif gender1 is cls.neutral and gender2 is cls.masculine:
            return cls.masculine

        elif gender1 is cls.neutral and gender2 is cls.feminine:
            return cls.feminine

        elif gender1 is cls.neutral and gender2 is cls.neutral:
            return cls.neutral

        else:
            return None


    @classmethod
    def genders_match(cls, gender1, gender2):
        match = gender1 in [gender2, cls.neutral] \
                or gender2 is cls.neutral
        return match
