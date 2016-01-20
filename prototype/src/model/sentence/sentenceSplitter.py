# -*- coding: utf-8 -*-

import re

from src.model.sentence.sentence import Sentence
from src.model.tokenization.token import Token
from src.utils.textCleaner import TextCleaner


class SentenceSplitter:
    def __init__(self):
        pass

    # TODO: Think again these parameters: text / paragraph / both?
    def sentences_in(self, text, paragraph=None):

        text = text.decode("utf-8")
        text = self.replace_strange_chars(text)
        split_text = self.split(text)
        texts = [each.strip().encode("utf-8") for each in split_text]

        non_empty_texts = filter(lambda p_text: p_text != '' and text is not None, texts)
        sentences = self.to_sentences(non_empty_texts, text, paragraph)

        return sentences

    def replace_strange_chars(self, text):
        text = text.replace(u'\xab', u'"').replace(u'\xbb', u'"')
        text = text.replace(u'«', u'"').replace(u'»', u'"')
        text = text.replace(u'/', u'-')
        text = text.replace(u'“', u'"').replace(u'”', u'"')
        text = text.replace(u'‘', u'"').replace(u'’', u'"')
        text = text.replace(u'“', u'"').replace(u'”', u'"')
        return text

    # Dirty
    def split(self, text):
        def default_replace(p_text, index, match):
            return p_text[index:match.end(1)] + match.group(2)

        validator = lambda match: not self.is_number(match) \
                                  and self.is_valid_delimiter_before_period(match.group(1))

        texts = re.split(self.delimiters, text, re.U)
        reg_exp = "(\w+|[^A-Za-z0-9])(\.)(?=[^\.])"
        texts_list = [self.split_by(reg_exp, text, default_replace, validator) for text in texts]
        texts = sum(texts_list, [])

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
    def split_by(self, regex, text, append_method, validator=lambda match: True):
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

    # TODO: Think again these parameters: text / paragraph / both?
    def to_sentences(self, texts, source, paragraph=None):
        sentences = [Sentence(text, paragraph) for text in texts]

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

    abbreviation_re = ("^(jr|mr|inc|ltd|co|ing|lic|dr|dra|arq|mag|mg"
                       "|phd|ph|prof|excmo|excma|mrs|gmbh|md|mons|cap"
                       "|tte|col|lt|sgt|cnel|gral|brig|pref|prof|sr|sra"
                       "|srta|dir|etc|fed|ee|uu|h|d|ms|s|a|sa|srl|r|l)$")

    abbreviation_regex = re.compile(abbreviation_re, re.U | re.I)

    delimiters = re.compile(ur"""[!\?]\s+"""
                            ur"""|(?=\.$)"""
                            ur"""|\n"""
                            ur"""|, ?y\b"""
                            ur"""|, ?pero\b"""
                            ur"""|, ?entonces"""
                            ur"""|, ?sin embargo\b"""
                            ur"""|, ?no obstante"""
                            ur"""|;"""
                            ur"""|\.\.\."""
                            ur"""|, ?pues\b""", re.U | re.I)

    textCleaner = TextCleaner()
