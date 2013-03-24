#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
from utils.logger_utils import *

pid = str(os.getpid())
pidfile = "/tmp/sentitext.pid"
file(pidfile, 'w').write(pid)

import re, web, codecs, json, logging
import entinews

logger    = get_logger('service')

urls = (
   '/entinews/(.+)', 'EntiNews'
)

app = web.application(urls, globals())

class EntiNews:
   def GET(self, text):
      logger.info('.'*80); logger.info("input text: %s" % text)

      entities = entinews.extract_entities(text)

      result = {}
      result["entities"] = []

      for entity in entities:
         logger.info(u"%s | %s | %s" % (entity, entity.head, entity.msi))
         result["entities"].append({"entity": entity.__str__(),
                                    "head": entity.head.__str__(),
                                    "full msi": entity.msi,
                                    "msi": entity.filtered_msi})
         logger.info(u"result: %s" % result)
      return json.dumps(result)

if __name__ == "__main__":
    print "launching..."
    app.run()
