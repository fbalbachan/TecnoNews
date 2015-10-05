# -*- coding: utf-8 -*-

from flask_restful_swagger import swagger
from flask_restful import fields
from flask import Flask

@swagger.model
class TextAnalyze(Flask.request_class):
    resource_fields = {
        'text': fields.String()
    }

@swagger.model
class Analyzer(Flask.response_class):
    resource_fields = {
        'paragraph': 	fields.String(),
        'sentences': 	fields.List(fields.String),
        'tagged_text': 	fields.String()
    }
