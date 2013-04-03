#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, sys, re
from utils.logger_utils import *

pid = str(os.getpid())
pidfile = "/tmp/entinews.pid"
file(pidfile, 'w').write(pid)

import re, web, codecs, json, logging
import entinews

logger    = get_logger('webapp/service')

urls = (
   '/favicon.ico',   'favicon',
   '/entinews/sentence/entities/(.+)', 'EntiNews',
   '/entinews/view/sentence/entities/(.+)', 'EntiNewsPretty'
)

app = web.application(urls, globals())

class favicon: 
   def GET(self): 
      f = open("webapp/static/favicon.ico", 'rb') 
      return f.read() 

class EntiNews:
   def GET(self, input_sentence):
      logger.info('.'*80); logger.info("input sentence: %s" % input_sentence)

      sentence = entinews.parse_sentence(input_sentence)
      entities = entinews.extract_entities(sentence)

      result = {}
      result["input sentence"] = sentence.input_sentence
      result["entities"] = []

      for entity in entities:
         logger.info(u"%s | %s | %s" % (entity, entity.head, entity.msi))
         result["entities"].append({"entity": entity.__str__(),
                                    "msi": entity.msi})
         logger.info(u"result: %s" % result)
      return json.dumps(result, ensure_ascii=False).encode('utf-8')

class EntiNewsPretty:
   def GET(self, input_sentence):
      logger.info('.'*80); logger.info("input sentence: %s" % input_sentence)

      sentence = entinews.parse_sentence(input_sentence)
      entities = entinews.extract_entities(sentence)
      freeling output = sentence.pretty_freeling_output

      return web.template.render('views').entities(entities, freeling_output)

if __name__ == "__main__":
    print "launching..."
    app.run()
