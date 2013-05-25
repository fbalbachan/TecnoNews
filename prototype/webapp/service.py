#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, sys, re
from utils.logger_utils import *

WEBAPP_PATH = open('webapp/webapp_path','r').read().strip('\n').strip('WEBAPP_PATH=')

pid = str(os.getpid())
pidfile = '/tmp/entinews.pid'
file(pidfile, 'w').write(pid)

import re, web, codecs, json, logging
import entinews

logger    = get_logger('webapp/service')

urls = (
   '/favicon.ico', 'favicon',
   '/sentence/tree/(.+)', 'EntiNewsParseTree',
   '/sentence/(.+)', 'EntiNews',
)

app = web.application(urls, globals())

class favicon: 
   def GET(self): 
      f = open('webapp/static/favicon.ico', 'rb') 
      return f.read() 

class EntiNews:
   def GET(self, input_sentence):
      logger.info('.'*80); logger.info('input sentence: %s' % input_sentence)

      sentence = Sentence(input_sentence)
      entities = sentence.entities
      subject = sentence.subject
      verb = sentence.verb

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

      if sentence.od:
         result['od'] = sentence.od.__str__().decode('utf-8')
         result['od.msi'] = sentence.od.msi
      else:
         result['od'] = None
         result['od.msi'] = None

      if sentence.OI:
         result['oi'] = sentence.od.__str__().decode('utf-8')
         result['oi.msi'] = sentence.od.msi
      else:
         result['oi'] = None
         result['oi.msi'] = None

      # return json.dumps(result, ensure_ascii=False).encode('utf-8')
      return web.template.render(WEBAPP_PATH + 'templates/').entinews(result)
      # return page(result)

class EntiNewsParseTree:
   def GET(self, input_sentence):
      logger.info('.'*80); logger.info('input sentence: %s' % input_sentence)

      sentence = Sentence(input_sentence)
      entities = sentence.entities
      parse_tree = sentence.pretty_freeling_output

      return web.template.render('templates').entities(input_sentence, entities, parse_tree)
      # return parse_tree

if __name__ == '__main__':
    print 'launching...'
    app.run()
