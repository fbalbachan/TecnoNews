__author__ = 'Martin Carames'
#from enum import Enum

# class Animity(Enum):
#     animated = 1
#     bianimate = 2
#     inanimate = 3
#
#     @classmethod
#     def most_specific(self, anim1, anim2):
#         if anim1 is self.animated and anim2 is self.animated:
#             return self.animated
#         elif anim1 is self.bianimate and anim2 is self.bianimate:
#             return self.bianimate
#         elif anim1 is self.inanimate and anim2 is self.inanimate:
#             return self.inanimate
#         elif anim1 is self.animated and anim2 is self.bianimate:
#             return self.animated
#         elif anim1 is self.bianimate and anim2 is self.animated:
#             return self.animated
#         elif anim1 is self.bianimate and anim2 is self.inanimate:
#             return self.inanimate
#         elif anim1 is self.inanimate and anim2 is self.bianimate:
#             return self.inanimate
#         else:
#             return None

def most_specific(anim1, anim2):
     if anim1 is "animated" and anim2 is "animated":
         return "animated"
     elif anim1 is "bianimate" and anim2 is "bianimate":
         return "bianimate"
     elif anim1 is "inanimate" and anim2 is "inanimate":
         return "inanimate"
     elif anim1 is "animated" and anim2 is "bianimate":
         return "animated"
     elif anim1 is "bianimate" and anim2 is "animated":
         return "animated"
     elif anim1 is "bianimate" and anim2 is "inanimate":
         return "inanimate"
     elif anim1 is "inanimate" and anim2 is "bianimate":
         return "inanimate"

def animities_match(anim1, anim2):
    match = anim1 == anim2 \
            or anim1 == "bianimate" \
            or anim2 == "bianimate"
    return match
