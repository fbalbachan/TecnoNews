# -*- coding: utf-8 -*-
import re
from src.model.sentence.sentence import *
from src.utils.textCleaner import *

class SentenceSplitter:
	def sentences_in(self, text):
		text = text.decode("utf-8")
		texts = [ text.strip().encode("utf-8") for text in self.split(text)]
		clean_texts = [ self.textCleaner.clean(text) for text in texts]
		non_empty_texts = filter(lambda text: text != u'' and text != None, clean_texts)
		s = self.to_sentences(non_empty_texts)
		print "sent", s
		return s

	def split(self, text):
		texts = re.split(self.delimiters, text, re.U)
		return sum([ self.split_by_period(text) for text in texts ], [])

	def split_by_period(self, text):
		start_index = 0
		texts = []
		for match in re.finditer("(\w+)\.\s", text, re.U):
			if self.is_valid_delimiter_before_period(match.group(1)):
				texts.append(text[start_index:match.end(1)])
				start_index = match.end()
		if start_index < len(text):
			texts.append(text[start_index:])
		return texts

	def is_valid_delimiter_before_period(self, string):
		return not (bool(self.abbreviation_regex.match(string)) or bool(re.match("^[A-Z]$", string)))

	def to_sentences(self, texts):
		return [ Sentence(text) for text in texts ]

	abbreviation_regex = re.compile("^(jr|mr|inc|ltd|co|ing|lic|dr|dra|arq|mag|phd|ph|prof|excmo|excma|mrs|gmbh|md|mons|cap|tte|col|lt|sgt|cnel|gral|brig|pref|prov|sr|sra|srta|dir|etc|fed)$", re.U | re.I)
	delimiters = re.compile(ur"""\?+|\.$|\n|,pero|, pero|:\s+|, y|,y|,mientras|, mientras|,entonces|, entonces|, aunque|,aunque|, sin embargo|,sin embargo|, no obstante|,no obstante|!+|; |\.\.\.|, pues|,pues""", re.U|re.I)
	textCleaner = TextCleaner()
