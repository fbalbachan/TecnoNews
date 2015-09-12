# -*- coding: utf-8 -*-

from flask_restful_swagger import swagger
from flask_restful import fields

@swagger.model
class TextAnalyze:
	resource_fields = {
		'text': fields.String()
	}

@swagger.model
class Analyzer:
	resource_fields = {
		'paragrapgh': fields.String(),
		'sentences': fields.List(fields.String),
		'tagged_text': fields.String()
	}
