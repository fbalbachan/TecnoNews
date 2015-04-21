__author__ = 'Martin Carames Abente'

from enum import Enum


class NumberEnum(Enum):
    singular = "singular"
    plural = "plural"
    invariable = "invariable"
    impersonal_invariable = "impersonal/invariable"

    @classmethod
    def most_specific(cls, number1, number2):
        if number1 is cls.singular and number2 is cls.singular:
            return cls.singular

        elif number1 is cls.singular and number2 is cls.invariable \
                or number1 is cls.invariable and number2 is cls.singular:
            return cls.singular

        elif number1 is cls.singular and number2 is cls.impersonal_invariable \
                or number1 is cls.impersonal_invariable and number2 is cls.singular:
            return cls.singular

        elif number1 is cls.plural and number2 is cls.plural:
            return cls.plural

        elif number1 is cls.plural and number2 is cls.invariable \
                or number1 is cls.invariable and number2 is cls.plural:
            return cls.plural

        elif number1 is cls.plural and number2 is cls.impersonal_invariable \
                or number1 is cls.impersonal_invariable and number2 is cls.plural:
            return cls.plural

        elif number1 is cls.invariable and number2 is cls.impersonal_invariable \
                or number1 is cls.impersonal_invariable and number2 is cls.invariable:
            return cls.invariable

        elif number1 is cls.impersonal_invariable and number2 is cls.impersonal_invariable:
            return cls.impersonal_invariable

        else:
            return None

    @classmethod
    def numbers_match(cls, number1, number2):
        match = number1 in [number2, cls.invariable, cls.impersonal_invariable] \
                or number2 in [cls.invariable, cls.impersonal_invariable]
        return match
