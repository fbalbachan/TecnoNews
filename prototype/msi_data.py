#!/usr/bin/env python
#-*- coding: utf-8 -*-

word_category = {"A": u"adjetivo",
                 "R": u"adverbio",
                 "D": u"determinante",
                 "N": u"nombre",
                 "V": u"verbo",
                 "P": u"pronombre",
                 "C": u"conjunción",
                 "I": u"interjección",
                 "F": u"puntuación",
                 "Z": u"cifra",
                 "W": u"fecha/hora"}

attribute_map = {"A": {1: ("type", {"Q": u"calificativo", "O": u"ordinal", "0": None}),
                       2: ("grade", {"0" : None, "A": u"aumentativo", "C": u"diminutivo", "S": u"superlativo"}),
                       3: ("gender", {"M": u"masculino", "F": u"femenino", "C": u"común"}),
                       4: ("number", {"S": u"singular", "P": u"plural", "N": u"invariable"}),
                       5: ("function", {"0": None, "P": u"participio"})},
                 
                 "R": {1: ("type", {"G": u"general", "N": u"negativo"})},

                 "D": {1: ("type", {"D": u"demostrativo", "P": u"posesivo", "T": "interrogativo", "E": u"exclamativo", "I": u"indefinido", "A": u"artículo"}),
                       2: ("person", {"1" : u"primera", "2": u"segunda", "3": u"tercera"}),
                       3: ("gender", {"M": u"masculino", "F": u"femenino", "C": u"común", "N": u"neutro"}),
                       4: ("number", {"S": u"singular", "P": u"plural", "N": u"invariable"}),
                       5: ("owner", {"S": u"singular", "P": u"plural"})},

                 "N": {1: ("type", {"C": u"común", "P": u"propio"}),
                       2: ("gender", {"M": u"masculino", "F": u"femenino", "C": u"común"}),
                       3: ("number", {"S": u"singular", "P": u"plural", "N": u"invariable"}),
                       45: ("semantic_classification", {"SP": u"persona", "G0": u"lugar", "00": u"organización", "V0": u"otros"}), # ¿O0 o 00?
                       6: ("grade", {"A": u"aumentativo", "D": u"diminutivo", "0": None})},

                 "V": {1: ("category", {"V": u"verbo"}),
                       2: ("type", {"M": u"principal", "A": u"auxiliar", "S": u"semiauxiliar"}),
                       3: ("mode", {"I": u"indicativo", "S": u"subjuntivo", "M": u"imperativo", "N": u"infinitivo", "G": u"gerundio", "P": u"participio"}),
                       4: ("time", {"P": u"presente", "I": u"imperfecto", "F": u"futuro", "S": u"pasado", "C": u"condicional", "0": None}),
                       5: ("person", {"1" : u"primera", "2": u"segunda", "3": u"tercera"}),
                       6: ("number", {"S": u"singular", "P": u"plural"}),
                       7: ("gender", {"M": u"masculino", "F": u"femenino"})},

                 "P": {1: ("type", {"P": u"personal", "D": u"demostrativo", "X": u"posesivo", "I": u"indefinido", "T": u"interrogativo", "R": u"relativo", "E": u"exclamativo"}),
                       2: ("person", {"1" : u"primera", "2": u"segunda", "3": u"tercera"}),
                       3: ("gender", {"M": u"masculino", "F": u"femenino", "C": u"común", "N": u"neutro"}),
                       4: ("number", {"S": u"singular", "P": u"plural", "N": u"impersonal/invariable"}),
                       5: ("case", {"N": u"nominativo", "A": u"acusativo", "D": u"dativo", "O": u"oblicuo"}),
                       6: ("owner", {"S": u"singular", "P": u"plural"}),
                       7: ("politeness", {"P": u"polite"})},

                 "C": {1: ("type", {"C": u"coordinada", "S": u"subordinada"}),
                       2: ("person", {"1" : u"primera", "2": u"segunda", "3": u"tercera"}),
                       3: ("gender", {"M": u"masculino", "F": u"femenino", "C": u"común", "N": u"neutro"}),
                       4: ("number", {"S": u"singular", "P": u"plural", "N": u"impersonal/invariable"}),
                       5: ("case", {"N": u"nominativo", "A": u"acusativo", "D": u"dativo", "O": u"oblicuo"}),
                       6: ("owner", {"S": u"singular", "P": u"plural"}),
                       7: ("politeness", {"P": u"polite"})},
                       
                 "I": {1: ("category", {"S": u"adposición"}),
                       2: ("type", {"P": u"preposición"}),
                       3: ("form", {"S" : u"simple", "C": u"contraída"}),
                       4: ("gender", {"M": u"masculino"}),
                       5: ("number", {"S": u"singular"})},
                       
                 "F": {1: ("category", {"Z": u"cifra"}),
                       2: ("type", {"d": u"partitivo", "m": u"moneda", "p": u"porcentaje", "u": u"unidad"})},
                             
                 "W": {}

                }