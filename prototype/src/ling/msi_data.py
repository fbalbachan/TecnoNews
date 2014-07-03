#!/usr/bin/env python
#-*- coding: utf-8 -*-

word_category = {"A": u"adjective",
                 "R": u"adverb",
                 "D": u"determinant",
                 "N": u"noun",
                 "V": u"verb",
                 "P": u"pronoun",
                 "C": u"conjunction",
                 "I": u"interjection",
                 "S": u"adposition",
                 "F": u"punctuation",
                 "Z": u"number",
                 "W": u"date/time"}

attribute_map = {"A": {1: ("type", {"Q": u"calificative", "O": u"ordinal", "0": None}),
                       2: ("grade", {"0" : None, "A": u"augmentative", "C": u"diminutive", "S": u"superlative"}),
                       3: ("gender", {"M": u"masculine", "F": u"feminine", "C": u"neutral"}),                   # u"common"
                       4: ("number", {"S": u"singular", "P": u"plural", "N": u"invariable"}),
                       5: ("function", {"0": None, "P": u"participle"})},

                 "R": {1: ("type", {"G": u"general", "N": u"negative"})},

                 "D": {1: ("type", {"D": u"demostrative", "P": u"possesive", "T": "interrogative", "E": u"exclamative", "I": u"indefinite", "A": u"articulo"}),
                       2: ("person", {"1" : 1, "2": 2, "3": 3, "0": None}),
                       3: ("gender", {"M": u"masculine", "F": u"feminine", "C": u"neutral", "N": u"neutral"}),  # u"common"
                       4: ("number", {"S": u"singular", "P": u"plural", "N": u"singular"}),                     # u"invariable"
                       5: ("owner", {"S": u"singular", "P": u"plural", "0": None})},

                 "N": {1: ("type", {"C": u"common", "P": u"proper"}),
                       2: ("gender", {"M": u"masculine", "F": u"feminine", "C": u"common", "0": u"neutral"}), # <- 0: es NP
                       3: ("number", {"S": u"singular", "P": u"plural", "N": u"invariable", "0": u"singular"}),
                       45: ("semantic_classification", {"SP": u"person", "G0": u"place", "O0": u"organization", "V0": u"other", "00": None}),
                       6: ("grade", {"A": u"augmentative", "D": u"diminutive", "0": None})},

                 "V": {1: ("type", {"M": u"main", "A": u"auxiliar", "S": u"semiauxiliar"}),
                       2: ("mode", {"I": u"indicative", "S": u"subjuntive", "M": u"imperative", "N": u"infinitive", "G": u"gerundio", "P": u"participio"}),
                       3: ("time", {"P": u"presente", "I": u"imperfecto", "F": u"futuro", "S": u"pasado", "C": u"condicional", "0": u"singular"}),     # None
                       4: ("person", {"1" : 1, "2": 2, "3": 3, "0": None}),
                       5: ("number", {"S": u"singular", "P": u"plural", "0": None}),
                       6: ("gender", {"M": u"masculine", "F": u"feminine", "0": None})},

                 "P": {1: ("type", {"P": u"personal", "D": u"demostrative", "X": u"possesive", "I": u"indefinite", "T": u"interrogative", "R": u"relative", "E": u"exclamative", "0": None}),
                       2: ("person", {"1" : 1, "2": 2, "3": 3, "0": None}),
                       3: ("gender", {"M": u"masculine", "F": u"feminine", "C": u"neutral", "N": u"neutral", "0" : None}), # u"common"
                       4: ("number", {"S": u"singular", "P": u"plural", "N": u"impersonal/invariable", "0" : None}),
                       5: ("case", {"N": u"nominative", "A": u"acusative", "D": u"dative", "O": u"oblicuo", "0": None}),
                       6: ("owner", {"S": u"singular", "P": u"plural", "0": None}),
                       7: ("politeness", {"P": u"polite", "0": None})},

                 "C": {1: ("type", {"C": u"coordinated", "S": u"subordinated"}),
                       2: ("person", {"1" : 1, "2": 2, "3": 3}),
                       3: ("gender", {"M": u"masculine", "F": u"feminine", "C": u"neutral", "N": u"neutral"}), # u"common"
                       4: ("number", {"S": u"singular", "P": u"plural", "N": u"impersonal/invariable"}),
                       5: ("case", {"N": u"nominative", "A": u"acusative", "D": u"dative", "O": u"oblique"}),
                       6: ("owner", {"S": u"singular", "P": u"plural"}),
                       7: ("politeness", {"P": u"polite"})},

                 "I": {},

                 "S": {1: ("type", {"P": u"preposition"}),
                       2: ("form", {"S" : u"simple", "C": u"contracted"}),
                       3: ("gender", {"M": u"masculine", "0": None}),
                       4: ("number", {"S": u"singular", "0": None})},

                 # Esto parece ser incorrercto.
                 #"F": {1: ("category", {"Z": u"number"}),
                 #      2: ("type", {"d": u"partitive", "m": u"money", "p": u"percentage", "u": u"unit"})},
                 "F": {1: ("type", {"p": u".", "c" : u",", "s" : u"abbreviation", "i" : "?", "a" : "!" }),
                       2: ("function", { "a": "open", "t" : "close" })}, # Completar

                 "W": {},

                 "Z": {1: ("type", {"d": "partitive", "m": "currency", "p": "percentage", "u": "unit"})}
                }
