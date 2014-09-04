#!/usr/bin/env python
#-*- coding: utf-8 -*-

word_category = {"A": "adjective",
                 "R": "adverb",
                 "D": "determinant",
                 "N": "noun",
                 "V": "verb",
                 "P": "pronoun",
                 "C": "conjunction",
                 "I": "interjection",
                 "S": "adposition",
                 "F": "punctuation",
                 "Z": "number",
                 "W": "date/time"}

attribute_map = {"A": {1: ("type", {"Q": "calificative", "O": "ordinal", "0": None}),
                       2: ("grade", {"0" : None, "A": "augmentative", "C": "diminutive", "S": "superlative"}),
                       3: ("gender", {"M": "masculine", "F": "feminine", "C": "neutral"}),                   # "common"
                       4: ("number", {"S": "singular", "P": "plural", "N": "invariable"}),
                       5: ("function", {"0": None, "P": "participle"})},

                 "R": {1: ("type", {"G": "general", "N": "negative"})},

                 "D": {1: ("type", {"D": "demostrative", "P": "possesive", "T": "interrogative", "E": "exclamative", "I": "indefinite", "A": "articulo"}),
                       2: ("person", {"1" : 1, "2": 2, "3": 3, "0": None}),
                       3: ("gender", {"M": "masculine", "F": "feminine", "C": "neutral", "N": "neutral"}),  # "common"
                       4: ("number", {"S": "singular", "P": "plural", "N": "singular"}),                     # "invariable"
                       5: ("owner", {"S": "singular", "P": "plural", "0": None})},

                 "N": {1: ("type", {"C": "common", "P": "proper"}),
                       2: ("gender", {"M": "masculine", "F": "feminine", "C": "common", "0": "neutral"}), # <- 0: es NP
                       3: ("number", {"S": "singular", "P": "plural", "N": "invariable", "0": "singular"}),
                       45: ("semantic_classification", {"SP": "person", "G0": "place", "O0": "organization", "V0": "other", "00": None}),
                       6: ("grade", {"A": "augmentative", "D": "diminutive", "0": None})},

                 "V": {1: ("type", {"M": "main", "A": "auxiliar", "S": "semiauxiliar"}),
                       2: ("mode", {"I": "indicative", "S": "subjuntive", "M": "imperative", "N": "infinitive", "G": "gerundio", "P": "participio"}),
                       3: ("time", {"P": "presente", "I": "imperfecto", "F": "futuro", "S": "pasado", "C": "condicional", "0": "singular"}),     # None
                       4: ("person", {"1" : 1, "2": 2, "3": 3, "0": None}),
                       5: ("number", {"S": "singular", "P": "plural", "0": None}),
                       6: ("gender", {"M": "masculine", "F": "feminine", "0": None})},

                 "P": {1: ("type", {"P": "personal", "D": "demostrative", "X": "possesive", "I": "indefinite", "T": "interrogative", "R": "relative", "E": "exclamative", "0": None}),
                       2: ("person", {"1" : 1, "2": 2, "3": 3, "0": None}),
                       3: ("gender", {"M": "masculine", "F": "feminine", "C": "neutral", "N": "neutral", "0" : None}), # "common"
                       4: ("number", {"S": "singular", "P": "plural", "N": "impersonal/invariable", "0" : None}),
                       5: ("case", {"N": "nominative", "A": "acusative", "D": "dative", "O": "oblicuo", "0": None}),
                       6: ("owner", {"S": "singular", "P": "plural", "C": "both", "0": None}),
                       7: ("politeness", {"P": "polite", "0": None})},

                 "C": {1: ("type", {"C": "coordinated", "S": "subordinated"}),
                       2: ("person", {"1" : 1, "2": 2, "3": 3}),
                       3: ("gender", {"M": "masculine", "F": "feminine", "C": "neutral", "N": "neutral"}), # "common"
                       4: ("number", {"S": "singular", "P": "plural", "N": "impersonal/invariable"}),
                       5: ("case", {"N": "nominative", "A": "acusative", "D": "dative", "O": "oblique"}),
                       6: ("owner", {"S": "singular", "P": "plural"}),
                       7: ("politeness", {"P": "polite"})},

                 "I": {},

                 "S": {1: ("type", {"P": "preposition"}),
                       2: ("form", {"S" : "simple", "C": "contracted"}),
                       3: ("gender", {"M": "masculine", "0": None}),
                       4: ("number", {"S": "singular", "0": None})},

                 "F": {"aa" : "¡", "at" : "!", "c" : ",", "ca" : "[", "ct" : "]", "d" : ":", "e" : '"', "g" : "-",
                       "h" : "/", "ia" : "¿", "it" : "?", "la" : "{", "lt" : "}", "p" : ".", "pa" : "(", "pt" : ")",
                       "ra" : "«", "rc" : "»", "s" : "...", "t" : "%", "x" : ";", "z" : "=+_" },

                 "W": {},

                 "Z": {1: ("type", {"d": "partitive", "m": "currency", "p": "percentage", "": "unit"})}
                }