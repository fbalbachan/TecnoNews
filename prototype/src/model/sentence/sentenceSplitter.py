# -*- coding: utf-8 -*-
import re

from src.model.sentence.sentence import Sentence
from src.model.tokenization.token import Token
from src.utils.textCleaner import TextCleaner


class SentenceSplitter:
    # TODO: Repensar parámetros: text o paragraph? o ambos?
	def sentences_in(self, text, paragraph = None):
		text = text.decode("utf-8")
		text = self.replace_strange_chars(text)

		texts = [ each.strip().encode("utf-8") for each in self.split(text)]
		non_empty_texts = filter(lambda text: text != '' and text != None, texts)
		return self.to_sentences(non_empty_texts, text, paragraph)

	def replace_strange_chars(self, text):
		return text.replace(u"“", '"').replace(u"”", '"') #.replace('"', "-")

	# Dirty
	def split(self, text):
		def replace_signs(text, index, match):
			signs = match.group(0)
			if "!" in signs and "?"  in signs:	replacement = "!?"
			elif "!" in signs: 					replacement = "!"
			else:								replacement = "?"

			return text[index:match.start(0)] + replacement

		validator = lambda match: \
			(not self.is_number(match)) and self.is_valid_delimiter_before_period(match.group(1))

		def default_replace(text, index, match):
			return text[index:match.end(1)] + match.group(2)

		texts = re.split(self.delimiters, text, re.U)
		texts = sum([ self.split_by("(\w+|[^A-Za-z0-9])(\.)(?=[^\.])", text, default_replace, validator) for text in texts ], [])
		#texts = sum([ self.split_by("[!\?]+[!\? ]*", text, replace_signs) for text in texts ], [])

		return texts

	def is_number(self, match):
		try:
			char = match.string[match.end()]
			int(char)

			string = match.group(0) + char
			float(string)
		except ValueError:
			return False
		return True

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

	# TODO: Repensar parámetros: text o paragraph? o ambos?
	def to_sentences(self, texts, source, paragraph = None):
		sentences = [ Sentence(text, paragraph) for text in texts ]

		end = 0

		for sentence in sentences:
			sentence_text = sentence.text.decode("utf-8")
			index = source.index(sentence_text)
			source = source[index + len(sentence_text):]

			index += end

			token = Token()
			token.append(index, index + len(sentence_text))

			sentence.token = token

			end = token.end()

		return sentences

	abbreviation_regex = re.compile("^(jr|mr|inc|ltd|co|ing|lic|dr|dra|arq|mag|mg|phd|ph|prof|excmo|excma|mrs|gmbh|md|mons|cap|tte|col|lt|sgt|cnel|gral|brig|pref|prof|sr|sra|srta|dir|etc|fed|ee|uu|h|d|ms|s|a|sa|srl|r|l)$", re.U | re.I)
	# delimiters = re.compile(ur"""[!\?]\s+|(?=\.$)|\n|, ?pero\b|:\s+|, ?y\b|, ?entonces|, ?sin embargo\b|, ?no obstante|;|\.\.\.|, ?pues\b""", re.U|re.I)
	delimiters = re.compile(ur"""[!\?]\s+|(?=\.$)|\n|, ?pero\b|, ?y\b|, ?entonces|, ?sin embargo\b|, ?no obstante|;|\.\.\.|, ?pues\b""", re.U|re.I)
	textCleaner = TextCleaner()
