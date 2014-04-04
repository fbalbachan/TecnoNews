# -*- coding: utf-8 -*-
from utils import tokenize


class TextCleaner:
    def clean(self, text):
        clean = tokenize.detroll(text)
        clean = tokenize.limpieza_inicial(clean)
        clean = tokenize.replace_repeated_letters(clean)
        return clean