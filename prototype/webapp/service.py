#!/usr/bin/python
# -*- coding: utf-8 -*-
from StringIO import StringIO
import os, web
from sys import exc_info
import sys
from traceback import format_exc, format_stack

from src.entinews import Entinews
from src.model.sentence import Sentence
from src.model.sentenceAnalyzer import SentenceAnalyzer
from src.webOutputUtils import WebOutputUtils


def write_pidfile():
	pid = str(os.getpid())
	pidfile = '/tmp/entinews.pid'
	file(pidfile, 'w').write(pid)

def analyze():
	try:
		web_input = web.input()
		input_text = web_input.text
		if type(input_text) == unicode: input_text = input_text.encode("utf-8") # unicode -> str (encoded)

		analyzer = SentenceAnalyzer()
		sentence = Sentence(input_text)
		analyzer.analyze(sentence)
		return sentence
	except Exception:
		return web.template.render().exception(format_exc(), "")

class Favicon_request:
	def GET(self):
		f = open('static/favicon.ico', 'rb')
		return f.read()

class Index_request:
	def GET(self):
		index = web.template.frender('templates/index.html')
		return index()
		#return web.template.render().index()

class Debug_request:
	def GET(self):
		output = StringIO("")
		sys.stdout = output
		sys.stderr = output
		analyze()
		return web.template.render().debug(output.getvalue())

class EntiNews_request:
	def GET(self):
		sentence = analyze()
		return web.template.render().test(sentence, WebOutputUtils())

### MAIN ###

if __name__ == '__main__':
	print 'launching...'

	urls = (
 	  '/favicon.ico', 'Favicon_request',
 	  '/result', 'EntiNews_request',
 	  '/', 'Index_request',
 	  '/debug', "Debug_request"
	)

	write_pidfile()

	app = web.application(urls, globals())
	app.run()
