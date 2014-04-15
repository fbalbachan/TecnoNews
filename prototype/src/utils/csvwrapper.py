#!/usr/bin/env python
#-*- coding:utf-8 -*-
import csv

def unicode_csv_reader(data, dialect=csv.excel, first_line_is_header=False, **kwargs):
    csv_reader = csv.reader(data, dialect=dialect, **kwargs)
    if first_line_is_header:
        csv_reader.next()
    for row in csv_reader:
        yield row
