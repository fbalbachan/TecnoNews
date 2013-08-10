#!/usr/bin/env python
#-*- coding: utf-8 -*-
import codecs
from utils.csvwrapper import *

def load_csv_test_file(csv_file):
    """in: csv file filename
       out: list of tuples with test lines
            e.g. [
                  ('input 1', 'expected result a1', 'expected result b1', ...),
                  ('input 2', 'expected result a2', 'expected result b2', ...),
                  ...
                 ]"""
    file_reader = unicode_csv_reader(codecs.open(csv_file, 'r', 'utf-8'), first_line_is_header=True, delimiter=',')
    return [test_tuple for test_tuple in file_reader if not(test_tuple[0].startswith('#'))]