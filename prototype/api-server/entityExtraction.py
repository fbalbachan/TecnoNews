# -*- coding: utf-8 -*-
from flask_restful_swagger import swagger

from src.model.sentilecto import Sentilecto
from src.utils.stringUtils import has_type_encoding
from models import EntitiesResponse
from flask_restful import Api, Resource, reqparse, marshal_with

__author__ = 'Martín Caramés Abente'


class EntityExtraction(Resource):

    sentilecto = Sentilecto()

    @swagger.operation(notes='Analyze the text and extract named & non-named entities. ---- NOTE: This v0.9 is an early release, expect v1.0 coming very soon. In it you\'ll find new resources and improved functionality.',
                       description='Natural Language Understanding / Sentiment Analysis service',
                       responseClass=EntitiesResponse,
                       nickname='get entities',
                       parameters=[
                                {
                                    "name":         "text",
                                    "description":  "Text to be Analyzed",
                                    "required":     True,
                                    "allowMultiple": False,
                                    "dataType":     "string",
                                    "paramType":    "path"
                                }
                            ],
                       responseMessages=[
                                {"code": 200, "message": "Entities properly extracted"},
                                {"code": 500, "message": "Bad response"}
                            ]
                      )
    @marshal_with(EntitiesResponse.resource_fields)
    def get(self, text):
        print "Hola Extraction"

        if has_type_encoding(text, str, 'UTF-8'):
            text = text.decode('UTF-8')

        try:
            analysis = self.sentilecto.analyze(text)

            analysis_results = \
                {
                    '0-Paragraph-Text':    analysis["paragraph"].text,
                    '1-Entity-Tagged-Text':  analysis["tagged_text"],
                    '2-Sentences':    [sentence.text for sentence in analysis["paragraph"].sentences]
                }

            response_value = analysis_results
            response_code = 200

        except Exception, e:
            response_value = {'type': 'ERROR', 'message': str(e)}
            response_code = 500,

        response = \
            (
                response_value,
                response_code,
                {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json; '
                    'charset=utf-8'
                }
            )

        return response

    def options (self, **args):
        return {'Allow': 'GET,PUT,POST,DELETE'}, \
               200, \
               {'Access-Control-Allow-Origin':     '*',
                'Access-Control-Allow-Methods':    'GET,PUT,POST,DELETE',
                'Access-Control-Allow-Headers':    'Content-Type'}
