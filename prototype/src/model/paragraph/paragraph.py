# -*- coding: utf-8 -*-
import re

from src.model.sentence.sentenceSplitter import SentenceSplitter
from src.utils.textCleaner import TextCleaner

debug_mode = False


class Paragraph:
    def __init__(self, sentences=None, text=""):
        if debug_mode: print "--> Paragraph.init()"
        self.sentences = sentences if sentences else []
        self.original_text = text
        self.parenthesis_positions_in_original_text = []
        self.parenthetic_dash_positions_in_original_text = []
        self.text = text

    def clauses(self):
        return sum([sentence.clauses for sentence in self.sentences], [])

    def entities(self):
        return sum([clause.all_entities() for clause in self.clauses()], [])

    def referents(self):
        return set([entity.referent for entity in self.entities()])

    def named_referents(self):
        return {referent for referent in self.referents() if referent.semantic_classification()}

    def clauses_for(self, referent):
        return filter(lambda clause: any( ( referent == entity.referent for entity in clause.all_entities()) ),
                      self.clauses())

    def facts_for(self, referent):
        return filter(lambda clause: clause.is_fact(), self.clauses_for(referent))

    @staticmethod
    def from_text(text):
        if debug_mode: print "--> Paragraph.from_text()"

        # TODO: Repensar desde la arquitectura si las sentences son de text o del párrafo,
        #       ya que Paragraph(sentences, text) puede ser redundante.
        #       Meanwhile, paragraph is a parameter (possibly redundant) of SentenceSplitter.sentences_in()

        paragraph = Paragraph([], text)
        paragraph._process_parenthesis()
        paragraph._process_parenthetic_dashes()

        sentences = SentenceSplitter().sentences_in(paragraph.text, paragraph)

        for sentence in sentences:
            sentence.text = Paragraph._preprocess_text(sentence.text)
        paragraph.sentences = sentences

        if debug_mode: print "<-- Paragraph.from_text() - Sentences retrieved: ", paragraph.sentences
        return paragraph

    def _process_parenthesis(self):

        # This regexp matches text between parenthesis. The text between parenthesis has to meet 2 conditions:
        # 1) atomic  = it has no '(', ')' chars at all
        # 2) complex = it has at most 1, balanced, inner pair. Like in: "Hi (how (are) you yoo)?".
        atom_par = r'\([^()]*\)'
        complex_par = r'\([^()]*({0})[^()]*\)'.format(atom_par)
        parenthesis_re = r'({0})|({1})'.format(atom_par, complex_par)

        iter_parenthesis = re.finditer(parenthesis_re, self.original_text)
        for parenthesis in iter_parenthesis:
            parenthesis_data = (parenthesis.group(), parenthesis.span())
            self.parenthesis_positions_in_original_text.append(parenthesis_data)

        self.text = re.sub(parenthesis_re, '', self.text)

    def _process_parenthetic_dashes(self):

        text = self.text

        # This regexp matches text between dashes (opening with ' -' and closing with '- ').
        # The text between dashes has to meet the following condition:  does not have: ['–']
        dash_enclosed_re = r' –(\S[^–]*\S|\S)– '
        iter_parenthetic_dash = re.finditer(dash_enclosed_re, self.original_text)
        for parenthetic_dash in iter_parenthetic_dash:
            span = parenthetic_dash.span()
            if span[1] > 0:
                span = (span[0], span[1]-1)
            parenthetic_dash_data = (parenthetic_dash.group()[0:-2], span)
            self.parenthetic_dash_positions_in_original_text.append(parenthetic_dash_data)

        text = re.sub(dash_enclosed_re, ' ', text)

        # This regexp matches text between an opening dash (' –') and a '.'.
        # The text in between has to meet the following condition:  does not have: ['–', '.']
        dash_period_enclosed_re = r' –(\S[^–.]*\S|\S)\.'
        iter_parenthetic_dash = re.finditer(dash_period_enclosed_re, self.original_text)
        for parenthetic_dash in iter_parenthetic_dash:
            span = parenthetic_dash.span()
            if span[1] > 0:
                span = (span[0], span[1]-1)
            parenthetic_dash_data = (parenthetic_dash.group()[0:-2], span)
            self.parenthetic_dash_positions_in_original_text.append(parenthetic_dash_data)

        text = re.sub(dash_period_enclosed_re, '.', text)

        self.text = text

    @staticmethod
    def _preprocess_text(text):

        tc = TextCleaner()
        preprocessed_text = tc.clean(text)
        return preprocessed_text
