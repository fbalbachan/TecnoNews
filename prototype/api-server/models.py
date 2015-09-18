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
    resource_fields = \
        {
            '0-Paragraph-Text':     fields.String(),
            '1-Entity-Tagged-Text': fields.String(),
            '2-Sentences':          fields.List(fields.String)
        }


@swagger.model
class DeepStructureResponse(Flask.response_class):

    svo_slots = \
        {
            '0-Subject': fields.String(),
            '1-Verb': fields.String(),
            '2-Direct-Object': fields.String(),
            '2-Equative': fields.String(),
            '2-Phrasal-Verb-Complement': fields.String(),
            '3-Indirect-Object-Experimenter': fields.String(),
            '4-Instrument-Company-Goal-Beneficiary': fields.String(),
            '5-Adjuncts': fields.String(),
            '6-Time': fields.String(),
            '7-Opinionated-Modal-Adverbs': fields.String()
        }

    deep_structure = \
        {
            '0-Global-Operators': fields.List(fields.String()),
            '1-SVO-Slots': fields.Nested(svo_slots)
        }

    clause = \
        {
            '0-Clause-Text':   fields.String(),
            '1-Clause-Order':  fields.String(),
            '2-Deep-Structure': fields.Nested(deep_structure)
        }

    sentence = \
        {
            '0-Sentence-Text':  fields.String(),
            '1-Sentence-Order': fields.Integer(),
            '2-Sentence-Clauses': fields.List(fields.Nested(clause))
        }

    resource_fields = \
        {
            '0-Paragraph-Text':            fields.String(),
            '1-Entity-Tagged-Text':   fields.String(),
            '2-Sentences':            fields.List(fields.Nested(sentence))
        }
