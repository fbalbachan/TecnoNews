# -*- coding: utf-8 -*-
import re
from src.model.sentence.sentence import *
from src.utils.textCleaner import *

class SentenceSplitter:
	def sentences_in(self, text):
		texts = [ text.strip() for text in self.split(text)]
		clean_texts = [ self.textCleaner.clean(text) for text in texts]
		non_empty_texts = filter(lambda text: text != u'' and text != None, texts)
		return self.to_sentences(non_empty_texts)

	def split(self, text):
		return re.split(self.delimiters, text, re.U)

	def to_sentences(self, texts):
		return [ Sentence(text) for text in texts ]

	delimiters = re.compile(ur"""\?+|\n|\. |\.$|,pero|, pero|:\s+|, y|,y|,mientras|, mientras|,entonces|, entonces|, aunque|,aunque|, sin embargo|,sin embargo|, no obstante|,no obstante|!+|; |\.\.\.|, pues|,pues""", re.U|re.I)
	textCleaner = TextCleaner()
