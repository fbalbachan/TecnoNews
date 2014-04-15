#-*- coding: utf-8 -*-
import os, ConfigParser

# Debería llamarse "FreelingParserClientParser"..
class FreelingClientParser:
	def parse(self, text):
		return self.get_client_output_for(text)

	def get_client_output_for(self, text):
		if type(text) != str: raise Exception("Solo se acepta unicode codificado a string.")

		config = self.config
		command = 'echo "%s" | ' + config["client"] + ' ' + config["host"] + ':' + config["parser_port"]

		raw_output = os.popen((command % text)).read()
		#return [line.strip() for line in raw_output.split('\n')]
		return raw_output.split('\n')

	def setup_config(self):
		Config = ConfigParser.ConfigParser()
		Config.read("config")
		self.config = dict(Config.items("freeling"))

	def __init__(self):
		self.setup_config()