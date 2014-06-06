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
		return self.to_sentences(non_empty_texts)

	def split(self, text):
		validator = lambda match: self.is_valid_delimiter_before_period(match.group(1))

		def replace_signs(text, index, match):
			signs = match.group(0)
			if "!" in signs and "?"  in signs:	replacement = "!?"
			elif "!" in signs: 					replacement = "!"
			else:								replacement = "?"

			return text[index:match.start(0)] + replacement

		def default_replace(text, index, match):
			return text[index:match.end(1)]

		texts = re.split(self.delimiters, text, re.U)
		texts = sum([ self.split_by("(\w+)\.\s", text, default_replace, validator) for text in texts ], [])
		texts = sum([ self.split_by("[!\?]+[!\? ]*", text, replace_signs) for text in texts ], [])
		return texts

	# Dirty
	def split_by(self, regex, text, append_method, validator = lambda match: True):
		start_index = 0
		texts = []
		for match in re.finditer(regex, text, re.U):
			if validator(match):
				texts.append(append_method(text, start_index, match))
				start_index = match.end()
		if start_index < len(text):
			texts.append(text[start_index:])
		return texts

	def is_valid_delimiter_before_period(self, string):
		return not (bool(self.abbreviation_regex.match(string)) or bool(re.match("^[A-Z]$", string)))

	def to_sentences(self, texts):
		return [ Sentence(text) for text in texts ]

	abbreviation_regex = re.compile("^(jr|mr|inc|ltd|co|ing|lic|dr|dra|arq|mag|phd|ph|prof|excmo|excma|mrs|gmbh|md|mons|cap|tte|col|lt|sgt|cnel|gral|brig|pref|prov|sr|sra|srta|dir|etc|fed)$", re.U | re.I)
	#|(?<=\?)\?*
	#[!\?]*(?<=(!\?|\?!))[!\?]*
	delimiters = re.compile(ur"""\.$|\n|,pero|, pero|:\s+|, y|,y|,mientras|, mientras|,entonces|, entonces|, aunque|,aunque|, sin embargo|,sin embargo|, no obstante|,no obstante|; |\.\.\.|, pues|,pues""", re.U|re.I)
	textCleaner = TextCleaner()
