#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, web

from entinews import Entinews
from model.sentence import Sentence

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
		return web.template.render().index()

class EntiNews_request:
	def GET(self):
		web_input = web.input()
		input_text = web_input.text
		entinews = Entinews()
		sentences = entinews.sentences_for(input_text)
		return web.template.render().entinews(sentences, input_text)

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
