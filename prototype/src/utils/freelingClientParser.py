#-*- coding: utf-8 -*-
import os, ConfigParser

# Debería llamarse "FreelingParserClientParser"..
class FreelingClientParser:
	def parse(self, text):
		text = self.normalized(text)
		return self.get_client_output_for(text)

	def get_client_output_for(self, text):
		config = self.config
		command = u'echo "%s" | ' + config["client"] + ' ' + config["host"] + ':' + config["parser_port"]

		raw_output = os.popen((command % text).encode('utf-8')).read().decode('utf-8')
		#return [line.strip() for line in raw_output.split('\n')]
		return raw_output.split('\n')

	def setup_config(self):
		Config = ConfigParser.ConfigParser()
		Config.read("config")
		self.config = dict(Config.items("freeling"))

	def normalized(self, text):
		if type(text) != unicode: text = text.decode('utf-8')
		return text

	def __init__(self):
		self.setup_config()