# -*- coding: utf-8 -*-

import unittest
import wikipedia as wk
from src.sentinews.news_rewriter import NewsRewriter
from src.sentinews.news_entry import NewsEntry


class TestNewsRewriter(unittest.TestCase):

  def testAddImage(self):
    wk.set_lang('es')
    wikipage
    nr = NewsRewriter(NewsEntry('','','',''))
    nr.insert_main_image(self, wikipage)
      

if __name__ == '__main__':
    unittest.main()
