#!/usr/bin/python
# -*- coding: utf-8 -*-
from StringIO import StringIO
import os, web
from sys import exc_info
from traceback import format_exc, format_stack

from src.entinews import Entinews
from src.model.sentence import Sentence
from src.model.sentenceAnalyzer import SentenceAnalyzer


def write_pidfile():
	pid = str(os.getpid())
	pidfile = '/tmp/entinews.pid'
	file(pidfile, 'w').write(pid)

class Favicon_request:
	def GET(self):
		f = open('static/favicon.ico', 'rb')
		return f.read()

class Index_request:
	def GET(self):
		index = web.template.frender('templates/index.html')
		return index()
		#return web.template.render().index()

class EntiNews_request:
	def GET(self):
		try:
			web_input = web.input()
			input_text = web_input.text
			if type(input_text) == unicode: input_text = input_text.encode("utf-8") # unicode -> str (encoded)

			analyzer = SentenceAnalyzer()
			sentence = Sentence(input_text)
			analyzer.analyze(sentence)
			return web.template.render().test(sentence)
 		except Exception:
 			return web.template.render().exception(format_exc(), "")

	def frame_info(self):
		frame_info = StringIO("")

		tb = exc_info()[2]
		while 1:
			if not tb.tb_next:
				break
			tb = tb.tb_next

		stack = []

		f = tb.tb_frame
		while f:
			stack.append(f)
			f = f.f_back

		stack.reverse()
		frame_info.write("Locals by frame, innermost last\n")
		for frame in stack:
			frame_info.write("\nFrame %s in %s at line %s\n" % (frame.f_code.co_name,
															frame.f_code.co_filename,
												 			frame.f_lineno))
			for key, value in frame.f_locals.items():
				frame_info.write("\t%20s = " % key)
				try:
					uni = unicode(str(value), "utf-8", "replace")
					frame_info.write(uni)
				except:
					frame_info.write("<ERROR WHILE PRINTING VALUE>")
				frame_info.write("\n")
		return frame_info.getvalue()

# 		entinews = Entinews()
# 		sentences = entinews.sentences_for(input_text)
# 		return web.template.render().entinews(sentences, input_text)

class EntiNewsParseTree_request:
	def GET(self, input_sentence):
		# logger.info('.'*80); logger.info('input sentence: %s' % input_sentence)

		sentence = Sentence(input_sentence)
		entities = sentence.entities
		parse_tree = sentence.pretty_freeling_output

		return web.template.render().entities(input_sentence, entities, parse_tree)
		# return parse_tree

### MAIN ###

if __name__ == '__main__':
	print 'launching...'

	urls = (
 	  '/favicon.ico', 'Favicon_request',
 	  '/sentence/tree/(.+)', 'EntiNewsParseTree_request',
 	  '/result', 'EntiNews_request',
 	  '/', 'Index_request',
	)

	write_pidfile()

	app = web.application(urls, globals())
	app.run()
