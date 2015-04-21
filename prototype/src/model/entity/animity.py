__author__ = 'Martin Carames'
from enum import Enum


class Animity(Enum):
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
    def animities_match(cls, anim1, anim2):
        """

        :rtype : bool
        """
        match = anim1 in [anim2, cls.bianimate] \
                or anim2 == cls.bianimate
        return match
