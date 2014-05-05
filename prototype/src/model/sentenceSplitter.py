# -*- coding: utf-8 -*-
from re import compile, match, split
import re
from src.model.sentence import *
from src.model.textCleaner import *

class SentenceSplitter:
	def sentences_in(self, text):
		texts = [ text.strip() for text in self.split(text)]
		clean_texts = [ self.textCleaner.clean(text) for text in texts]
		non_empty_texts = filter(lambda text: text != u'' and text != None, texts)
		return self.to_sentences(non_empty_texts)

	def split(self, text):
		return split(self.delimiters, text, re.U)

	def to_sentences(self, texts):
		return [ Sentence(self.add_final_punctuation_if_absent_to(text)) for text in texts ]

	def add_final_punctuation_if_absent_to(self, text):
		if not match(".*\W$", text.strip(" ")):
			text = text + "."
		return text

	delimiters = compile(ur"""\?+|\n|\. |,pero|, pero|:\s+|, y|,y|,mientras|, mientras|,entonces|, entonces|, aunque|,aunque|, sin embargo|,sin embargo|, no obstante|,no obstante|!+|; |\.\.\.|, pues|,pues""", re.U|re.I)
	textCleaner = TextCleaner()
