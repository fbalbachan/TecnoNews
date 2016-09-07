# -*- coding: utf-8 -*-

from flask_restful_swagger import swagger
from flask_restful import fields, marshal
from flask import Flask


@swagger.model
class EntitySentimentReportResponse(Flask.response_class):
    resource_fields = \
        {
            '0-Paragraph-Text':     fields.String(),
            '1-Entities-Report':    fields.List(fields.String)
        }


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
class RewritingResponse(Flask.response_class):
    resource_fields = \
        {
            '0-Source-Text'     : fields.String(),
            '1-Rewritten-Text'  : fields.String()
        }

@swagger.model
class SummarizingResponse(Flask.response_class):
    resource_fields = \
        {
            '0-Source-Text'     : fields.String(),
            '1-Summarized-Text'  : fields.String()
        }

@swagger.model
class SentimentAnalysisResponse(Flask.response_class):

    score = \
        {
            '0-Positive-Score':     fields.Float(),
            '1-Negative-Score':     fields.Float()
        }

    entity = \
        {
            '0-Entity-Text':              fields.String(),
            '1-Entity-Sentiment-Score':   fields.Nested(score)
        }

    clause = \
        {
            '0-Clause-Text':              fields.String(),
            '1-Clause-Sentiment-Score':   fields.Nested(score),
            '2-Entities':                 fields.List(fields.Nested(entity))
        }

    sentence = \
        {
            '0-Sentence-Text':              fields.String(),
            '1-Sentence-Sentiment-Score':   fields.Nested(score),
            '2-Clauses':                    fields.List(fields.Nested(clause))
        }

    resource_fields = \
        {
            '0-Paragraph-Text':             fields.String(),
            '1-Overall-Sentiment-Score':  fields.Nested(score),
            '2-Sentences':                  fields.List(fields.Nested(sentence))
        }


@swagger.model
class FactMiningResponse(Flask.response_class):

    score = \
        {
            '0-Clause-Order': fields.String(),
            '1-Score':        fields.String()
        }

    clause = \
        {
            '0-Clause-Order':       fields.String(),
            '1-Clause-Text':        fields.String(),
            '2-Clause-Normalized-Fact':    fields.String(),
            '3-Clause-Comparison':  fields.List(fields.Nested(score))
        }

    sentence = \
        {
            '0-Sentence-Order':     fields.Integer(),
            '1-Sentence-Text':      fields.String(),
            '2-Sentence-Clauses':   fields.List(fields.Nested(clause))
        }

    resource_fields = \
        {
            '0-Paragraph-Text':       fields.String(),
            '1-Sentences':            fields.List(fields.Nested(sentence))
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
            '0-Global-Operators':   fields.List(fields.String()),
            '1-SVO-Slots':          fields.Nested(svo_slots)
        }

    clause = \
        {
            '0-Clause-Text':        fields.String(),
            '1-Clause-Order':       fields.String(),
            '2-Deep-Structure':     fields.Nested(deep_structure)
        }

    morphosyntactic_info = \
        {
            '0-Entity-Name':    fields.String(),
            '1-Person':         fields.Integer(),
            '2-Gender':         fields.String(),
            '3-Number':         fields.String(),
            '4-Category':       fields.String(),
            '5-Animity':        fields.String(),
            '6-Semantic-Classification':  fields.String(),
            '7-Transitivity':   fields.String(),
            '8-Sentimental-Script-Class':  fields.String()
        }

    sentence = \
        {
            '0-Sentence-Text':      fields.String(),
            '1-Sentence-Order':     fields.Integer(),
            '2-Sentence-Clauses':   fields.List(fields.Nested(clause)),
            '3-Sentence-Morphosyntactic-Info': fields.List(fields.Nested(morphosyntactic_info))
        }

    resource_fields = \
        {
            '0-Paragraph-Text':            fields.String(),
            '1-Entity-Tagged-Text':   fields.String(),
            '2-Sentences':            fields.List(fields.Nested(sentence))
        }
