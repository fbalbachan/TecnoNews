#!/usr/bin/python
# -*- coding: utf-8 -*-
from StringIO import StringIO
import os, web
from sys import exc_info
import sys
from traceback import format_exc, format_stack

from src.model.paragraph.paragraph import Paragraph
from src.model.paragraph.paragraphAnalyzer import ParagraphAnalyzer
from src.model.sentence.sentence import Sentence
from src.model.sentence.sentenceAnalyzer import SentenceAnalyzer
from src.utils.webOutputUtils import WebOutputUtils


def write_pidfile():
	pid = str(os.getpid())
	pidfile = '/tmp/entinews.pid'
	file(pidfile, 'w').write(pid)

def analyze():
	try:
		web_input = web.input()
		input_text = web_input.text
		if type(input_text) == unicode: input_text = input_text.encode("utf-8") # unicode -> str (encoded)

		analyzer = ParagraphAnalyzer()
		paragraph = Paragraph.from_text(input_text)
		analyzer.analyze(paragraph)

		return paragraph.sentences
	except Exception:
		print format_exc()
		#web.template.render().exception(format_exc(), "")

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
		sentences = analyze()
		return web.template.render().test(sentences, WebOutputUtils())

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
