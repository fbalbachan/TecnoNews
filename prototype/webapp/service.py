#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, sys, re
from utils.logger_utils import *

pid = str(os.getpid())
pidfile = '/tmp/entinews.pid'
file(pidfile, 'w').write(pid)

import re, web, codecs, json, logging
import entinews

logger    = get_logger('webapp/service')

urls = (
   '/favicon.ico',                     'favicon',
   '/entinews/sentence/tree/(.+)',     'EntiNewsParseTree',
   # '/entinews/sentence/entities/(.+)', 'EntiNews',
    '/entinews/sentence/(.+)',         'EntiNews',
)

app = web.application(urls, globals())

class favicon: 
   def GET(self): 
      f = open('webapp/static/favicon.ico', 'rb') 
      return f.read() 

class EntiNews:
   def GET(self, input_sentence):
      logger.info('.'*80); logger.info('input sentence: %s' % input_sentence)

      sentence = entinews.parse_sentence(input_sentence)
      entities = entinews.extract_entities(sentence)
      subject = entinews.extract_subject(sentence)
      verb = sentence.verb
      sentence.verb_transitivity
      sentence.verb_script_class
      sentence.boxes

      result = {}
      result['input_sentence'] = sentence.input_sentence
      result['entities'] = []

      for entity in entities:
         result['entities'].append({'entity': entity.__str__().decode('utf-8'), 'msi': entity.msi})
         logger.info(u'result: %s' % result)

      result['subject'] = subject.__str__().decode('utf-8')
      result['subject.msi'] = subject.msi

      result['verb'] = verb.__str__()
      result['verb.msi'] = verb.msi
      result['transitivity'] = sentence.verb_transitivity
      result['script_class'] = sentence.verb_script_class

      # return json.dumps(result, ensure_ascii=False).encode('utf-8')
      page = web.template.frender('/home/ddellera/code/tecnolecto/entinews/prototype/webapp/templates/entinews.html')
      return page(result)

class EntiNewsParseTree:
   def GET(self, input_sentence):
      logger.info('.'*80); logger.info('input sentence: %s' % input_sentence)

      sentence = entinews.parse_sentence(input_sentence)
      entities = entinews.extract_entities(sentence)
      parse_tree = sentence.pretty_freeling_output

      return web.template.render('templates').entities(input_sentence, entities, parse_tree)
      # return parse_tree

if __name__ == '__main__':
    print 'launching...'
    app.run()
