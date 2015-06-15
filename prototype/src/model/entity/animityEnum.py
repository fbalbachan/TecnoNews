# -*- coding: utf-8 -*-
__author__ = 'Martin Caramés Abente'
from enum import Enum


class AnimityEnum(Enum):
    animated = "animated"
    bianimate = "bianimate"
    inanimate = "inanimate"

    @classmethod
    def most_specific(cls, animity1, animity2):

        if animity1 is cls.animated and animity2 is cls.animated:
            return cls.animated

        elif animity1 is cls.bianimate and animity2 is cls.bianimate:
            return cls.bianimate

        elif animity1 is cls.inanimate and animity2 is cls.inanimate:
            return cls.inanimate

        elif animity1 is cls.animated and animity2 is cls.bianimate \
                or animity1 is cls.bianimate and animity2 is cls.animated:
            return cls.animated

        elif animity1 is cls.bianimate and animity2 is cls.inanimate \
                or animity1 is cls.inanimate and animity2 is cls.bianimate:
            return cls.inanimate

        else:
            return None

    @classmethod
    def animities_match(cls, animity1, animity2):
        """

        :rtype : bool
        """
        match = animity1 in [animity2, cls.bianimate] \
               or animity2 == cls.bianimate
        return match
