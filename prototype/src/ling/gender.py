# -*- coding: utf-8 -*-
__author__ = 'Martin Caramés Abente'

from enum import Enum


class Gender(Enum):
    masculine = u"masculine"
    feminine = u"feminine"
    neutral = u"neutral"

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
