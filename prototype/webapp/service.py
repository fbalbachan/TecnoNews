#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, sys, re
from utils.logger_utils import *

WEBAPP_PATH = open('webapp/webapp_path','r').read().strip('\n').strip('WEBAPP_PATH=')
RANDOM_NUMBER_PATH = open('webapp/random_number_path','r').read().strip('\n').strip('RANDOM_NUMBER_PATH=')

pid = str(os.getpid())
pidfile = '/tmp/entinews.pid'
file(pidfile, 'w').write(pid)

import re, web, codecs, json, logging
from entinews import *

# logger    = get_logger('webapp/service')

urls = (
   '/favicon.ico', 'favicon',
   '/sentence/tree/(.+)', 'EntiNewsParseTree',
   '/sentence/' + RANDOM_NUMBER_PATH + '/(.+)', 'EntiNews',
)

app = web.application(urls, globals())

class favicon: 
   def GET(self): 
      f = open('webapp/static/favicon.ico', 'rb') 
      return f.read() 

class EntiNews:
   def GET(self, input_sentence):
      #logger.info('.'*80); logger.info('input sentence: %s' % input_sentence)

      sentence = Sentence(input_sentence)
      print sentence.evidence
      print sentence

      result = {}
      result['input_sentence'] = sentence.input_sentence
      result['entities'] = []

      for entity in sentence.entities:
         result['entities'].append({'entity': entity.__str__().decode('utf-8'), 'msi': entity.msi})
         # logger.info(u'result: %s' % result)

      if sentence.verb:
         result['verb'] = sentence.verb_final_form.__str__()
         result['verb.msi'] = sentence.verb.msi
         result['verb.transitivity'] = sentence.verb_transitivity
         result['verb.script_class'] = sentence.verb_script_class
      else:
         result['verb'] = None
         result['verb.msi'] = None
         result['verb.transitivity'] = None
         result['verb.script_class'] = None
         
      result['boxes'] = sentence.boxes

      if sentence.subject:
         result['subject'] = sentence.subject.__str__().decode('utf-8')
         result['subject.msi'] = sentence.subject.msi
         result['subject.entity_type'] = sentence.subject.entity_type
         result['subject.sentiment'] = u"↑ %.2f, ↓ %.2f" % sentence.subject.sentiment
      else:
         result['subject'] = None
         result['subject.msi'] = None
         result['subject.entity_type'] = None
         result['subject.sentiment'] = u" - "
         
      if sentence.od:
         result['od'] = sentence.od.__str__().decode('utf-8')
         result['od.msi'] = sentence.od.msi
      else:
         result['od'] = None
         result['od.msi'] = None

      if sentence.oi:
         result['oi'] = sentence.oi.__str__().decode('utf-8')
         result['oi.msi'] = sentence.oi.msi
      else:
         result['oi'] = None
         result['oi.msi'] = None

      if sentence.regimen:
         result['regimen'] = sentence.regimen.__str__().decode('utf-8')
         result['regimen.msi'] = sentence.regimen.msi
      else:
         result['regimen'] = None
         result['regimen.msi'] = None

      if sentence.equative:
         result['equative'] = sentence.equative.__str__().decode('utf-8')
         result['equative.msi'] = sentence.equative.msi
      else:
         result['equative'] = None
         result['equative.msi'] = None

      if sentence.adjuncts:
         result['adjuncts'] = ' | '.join([adjunct.__str__().decode('utf-8') for adjunct in sentence.adjuncts])
         result['adjuncts.msi'] = [adjunct.msi for adjunct in sentence.adjuncts]
      else:
         result['adjuncts'] = None
         result['adjuncts.msi'] = None

      # return json.dumps(result, ensure_ascii=False).encode('utf-8')
      return web.template.render(WEBAPP_PATH + 'templates/').entinews(result)
      # return page(result)

class EntiNewsParseTree:
   def GET(self, input_sentence):
      # logger.info('.'*80); logger.info('input sentence: %s' % input_sentence)

      sentence = Sentence(input_sentence)
      entities = sentence.entities
      parse_tree = sentence.pretty_freeling_output

      return web.template.render('templates').entities(input_sentence, entities, parse_tree)
      # return parse_tree

if __name__ == '__main__':
    print 'launching...'
    app.run()
