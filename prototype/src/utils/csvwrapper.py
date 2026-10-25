# -*- coding:utf-8 -*-

import csv


def unicode_csv_reader(data, dialect=csv.excel, first_line_is_header=False, **kwargs):
    csv_reader = csv.reader(data, dialect=dialect, **kwargs)
    if first_line_is_header:
        next(csv_reader)
    for row in csv_reader:
        yield row


def unicode_csv_writer(rows, file_obj, dialect=csv.excel, first_line_is_header=False, **kwargs):
    csv_writer = csv.writer(file_obj, dialect=dialect, **kwargs)
    csv_writer.writerows(rows)
