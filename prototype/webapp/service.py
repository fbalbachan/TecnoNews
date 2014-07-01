#!/usr/bin/python
# -*- coding: utf-8 -*-

from StringIO import StringIO
import logging
import os, web
import sys
import time

from src.model.paragraph.paragraph import Paragraph
from src.model.paragraph.paragraphAnalyzer import ParagraphAnalyzer
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
		return []
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
		logger = logging.getLogger("requests")
		logger.info(time.strftime("%d/%m/%Y %H:%M:%S") + "\t" + web.ctx["ip"] + "\t" + web.ctx["fullpath"])

		sentences = analyze()
		return web.template.render().test(sentences, WebOutputUtils())

### MAIN ###

def setup_loggers():
	logger_names = ["requests", "exceptions"]
	for name in logger_names:
		logger = logging.getLogger(name)
		logger.addHandler(logging.FileHandler(name + ".log"))
		logger.setLevel(logging.INFO)

if __name__ == '__main__':
	print 'launching...'

	urls = (
 	  '/favicon.ico', 'Favicon_request',
 	  '/result', 'EntiNews_request',
 	  '/', 'Index_request',
 	  '/debug', "Debug_request"
	)

	write_pidfile()
	setup_loggers()

	app = web.application(urls, globals())
	app.run()
