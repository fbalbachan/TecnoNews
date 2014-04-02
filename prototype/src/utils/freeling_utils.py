#!/usr/bin/env python
#-*- coding: utf-8 -*-
import os, ConfigParser

# Necesita ser remodelada adecuadamente
class FreelingAnalyzer(object):
	def parse(self):
		return self.freeling_output, self.freeling_pretty_output

	def tag(self):
		return self.freeling_output

	def store_freeling_output(self):
		config = self.config
		command = u'echo "%s." | ' + config["client"] + ' ' + config["host"] + ':' + config["parser_port"]
		
		self.freeling_pretty_output = os.popen((command % self.sentence).encode('utf-8')).read().decode('utf-8')
		self.freeling_output = [s.strip() for s in self.freeling_pretty_output.split('\n')]

	# TODO Inutil leerla en cada objeto. Pasar por constructor.
	def setup_config(self):
		Config = ConfigParser.ConfigParser()
		Config.read("config")
		self.config = dict(Config.items("freeling"))
	
	def set_sentence(self, sentence):
		print sentence
		print type(sentence)
		if type(sentence) != unicode: sentence = sentence.decode('utf-8')
		self.sentence = sentence
	
	def __init__(self, sentence):
		self.setup_config()
		self.set_sentence(sentence)
		self.store_freeling_output()
