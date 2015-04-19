__author__ = 'Martin Carames'
from enum import Enum


class Animity(Enum):
    animated = "animated"
    bianimate = "bianimate"
    inanimate = "inanimate"

    @classmethod
    def most_specific(cls, anim1, anim2):

        if anim1 is cls.animated and anim2 is cls.animated:
            return cls.animated

        elif anim1 is cls.bianimate and anim2 is cls.bianimate:
            return cls.bianimate

        elif anim1 is cls.inanimate and anim2 is cls.inanimate:
            return cls.inanimate

        elif anim1 is cls.animated and anim2 is cls.bianimate:
           return cls.animated

        elif anim1 is cls.bianimate and anim2 is cls.animated:
            return cls.animated

        elif anim1 is cls.bianimate and anim2 is cls.inanimate:
            return cls.inanimate

        elif anim1 is cls.inanimate and anim2 is cls.bianimate:
            return cls.inanimate

        else:
            return None


    @classmethod
    def animities_match(cls, anim1, anim2):
        match = anim1 in [anim2, cls.bianimate] \
                or anim2 == cls.bianimate
        return match
