__author__ = 'Martin Carames Abente'

from enum import Enum


class GenderEnum(Enum):
    masculine = "masculine"
    feminine = "feminine"
    neutral = "neutral"
    common = "common"

    @classmethod
    def most_specific(cls, gender1, gender2):
        if gender1 is cls.masculine and gender2 is cls.masculine:
            return cls.masculine

        elif gender1 is cls.masculine and gender2 is cls.neutral:
            return cls.masculine

        elif gender1 is cls.masculine and gender2 is cls.common:
            return cls.masculine

        elif gender1 is cls.feminine and gender2 is cls.feminine:
           return cls.feminine

        elif gender1 is cls.feminine and gender2 is cls.neutral:
            return cls.feminine

        elif gender1 is cls.feminine and gender2 is cls.common:
            return cls.feminine

        elif gender1 is cls.common and gender2 is cls.masculine:
            return cls.masculine

        elif gender1 is cls.common and gender2 is cls.feminine:
            return cls.feminine

        elif gender1 is cls.common and gender2 is cls.neutral:
            return cls.neutral

        elif gender1 is cls.neutral and gender2 is cls.common:
            return cls.neutral

        elif gender1 is cls.neutral and gender2 is cls.masculine:
            return cls.masculine

        elif gender1 is cls.neutral and gender2 is cls.feminine:
            return cls.feminine

        else:
            return None


    @classmethod
    def genders_match(cls, gender1, gender2):
        match = gender1 in [gender2, cls.neutral, cls.common] \
                or gender2 in [cls.neutral, cls.common]
        return match
