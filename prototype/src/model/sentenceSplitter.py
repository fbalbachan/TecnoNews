#!/usr/bin/python
# -*- coding: utf-8 -*-
import re

sentence_delimiters = re.compile(ur"""\?+|\n|\. |,pero|, pero|:\s+|, y|,y|,mientras|, mientras|,entonces|, entonces|, aunque|,aunque|, sin embargo|,sin embargo|, no obstante|,no obstante|!+|; |\.\.\.|, pues|,pues""", re.U|re.I)

def splitInSentences(input_text):
	input_sentences = [s.strip() for s in re.split(sentence_delimiters, input_text, re.U)]
	input_sentences = filter(lambda s: s != u'' and s != None, input_sentences)
	return input_sentences