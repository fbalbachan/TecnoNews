#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys

pid = str(os.getpid())
pidfile = "/tmp/sentitext.pid"
file(pidfile, 'w').write(pid)

import re, web, codecs, json, logging
import sentilecto

logger    = logging.getLogger('service')
handler   = logging.FileHandler('logs/servicio_sentitext.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler) 
logger.setLevel(logging.INFO)

urls = (
   '/result',        'SentiText',
   '/favicon.ico',   'favicon',
   '/sentitext',     'Index',
   '/',              'Index',
)

app = web.application(urls, globals())

class favicon: 
   def GET(self): 
      f = open("static/favicon.ico", 'rb') 
      return f.read() 

class Index:
   def GET(self):
      return web.template.render('templates').index()

class SentiText:
   def GET(self):
      i = web.input()
      inputtext = i.text
      logger.info('.'*80); logger.info("new text: %s" % inputtext)

      svos, entities = sentilecto.extract_entities(inputtext) # .split('\n'))
      entities = sentilecto.format_entities(entities)
      for entity in entities: logger.info("entity: %s (%d) | %s" % (entity, entity.sentence_id, '%d, %d)' % entity.get_sentiment()))
      # for svo in svos: logger.info("svo: %s" % svo.__str__())

      return web.template.render('templates').result(inputtext, svos, entities)

if __name__ == "__main__":
    print "launching..."
    app.run()
