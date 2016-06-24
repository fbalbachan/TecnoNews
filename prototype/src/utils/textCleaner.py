# -*- coding: utf-8 -*-
from src.utils import tokenize


class TextCleaner:

    def clean(self, text):
        clean = tokenize.limpieza_inicial(text)
        #clean = tokenize.replace_repeated_letters(clean)
        clean = tokenize.detroll(clean)
        return clean
