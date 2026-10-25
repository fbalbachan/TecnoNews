#-*- coding: utf-8 -*-
from src.decorators.singleton import singleton
import re

from langdetect import DetectorFactory, detect
from langdetect.lang_detect_exception import LangDetectException

# langdetect is probabilistic: a fixed seed gives the same answer for the same text
DetectorFactory.seed = 0


@singleton
class LanguageDetectorClient:
    """Language identification (spaCy has none built in), replacing FreeLing's lang ident server.
    Keeps its output format: [language_code, ''], or [''] when the language is unknown."""

    def __init__(self):
        self.calls_count = 0

    def health_check(self):
        expected = ['it', '']
        result = self.parse("Siamo fuori della coppa")
        return expected == result

    #TODO:refactor and rename it to lang_ident
    def parse(self, text):
        return self.get_client_output_for(text)

    def get_client_output_for(self, text):
        self.calls_count += 1

        if not isinstance(text, str):
            raise Exception("Must provide unicode strings.")

        text = re.sub(r"""[)|(|.|,|"|!|'|@|#|\$|%|^|&|\*]""", ' ', text)

        try:
            return [detect(text), '']
        except LangDetectException:
            return ['']
