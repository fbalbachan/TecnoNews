# -*- coding: utf-8 -*-

from flask_restful_swagger import swagger
from flask_restful import fields, marshal
from flask import Flask


@swagger.model
class TextAnalyze(Flask.request_class):
    resource_fields = {
        'text': fields.String()
    }


@swagger.model
class EntitiesResponse(Flask.response_class):
    resource_fields = {
        'paragraph': 	fields.String(),
        'sentences': 	fields.List(fields.String),
        'entity_tags': 	fields.String()
    }


@swagger.model
class DeepStructureResponse(Flask.response_class):

    svo_slot = \
        {
            'opinionated-modal-adverb': fields.String(),
            'subject': fields.String(),
            'verb': fields.String(),
            'direct-object': fields.String(),
            'indirect-object-experimenter': fields.String(),
            'phrasal-verb-complement': fields.String(),
            'equative': fields.String(),
            'instrument-company-goal-beneficiary': fields.String(),
            'adjuncts': fields.List(fields.String()),
            'time': fields.String()
        }

    deep_structure = \
        {
            'global_operators': fields.List(fields.String),
            'svo_slots': fields.List(fields.Nested(svo_slot))
        }

    clause = \
        {
            'entity_tagged_text': fields.String(),
            'deep_structure': fields.Nested(deep_structure)
        }

    sentence = \
        {
            'text':         fields.String(),
            'clauses':      fields.List(fields.Nested(clause))
        }

    resource_fields = \
        {
            'paragraph':    fields.String(),
            'sentences':    fields.List(fields.Nested(sentence))
        }
