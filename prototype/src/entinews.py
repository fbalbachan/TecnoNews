#!/usr/bin/python
# -*- coding: utf-8 -*-
import codecs
from model.sentence import *
from utils.logger_utils import *

logger = get_logger('entinews')


if __name__ == '__main__':

   if len(sys.argv) > 1:
      sentence = Sentence(sys.argv[1].decode('utf-8'))
      print sentence
      exit()

   while True:
      input_text = raw_input('> ').decode('utf-8')
      if input_text == 'q': exit()
      sentence = Sentence(input_text)
      print sentence
