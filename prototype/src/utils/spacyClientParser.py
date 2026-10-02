#-*- coding: utf-8 -*-
from src.nlp.freeling_tree import parse_lines
from src.nlp.spacy_engine import get_nlp


class SpacyClientParser:
    """Local replacement of the remote FreeLing parser: same output (FreeLing full-parse tree lines)."""

    def __init__(self):
        self.nlp = get_nlp()

    def health_check(self):
        # make a simple analysis to validate the spaCy model is loaded and the tree is well formed
        lines = self.parse("El perro come.")
        return lines[0] == "grup-verb_[" and "    +(come comer VMIP3S0 -)" in lines

    def parse(self, text):
        return self.get_client_output_for(text)

    def get_client_output_for(self, text):
        if not isinstance(text, str): raise Exception("The parse method only accept strings.")

        return parse_lines(self.nlp(text))
