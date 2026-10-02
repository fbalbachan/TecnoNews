# -*- coding: utf-8 -*-
from flask_restful_swagger import swagger

from src.model.sentilecto import Sentilecto
from src.utils.stringUtils import has_type_encoding
from models import SummarizingResponse
from flask_restful import Resource, marshal_with
from usersStorage import users_storage

from src.utils.textSummarizer import TextSummarizer


__author__ = 'Alexis Balbachan'


class Summarizing(Resource):

    def __init__(self):
        self.sentilecto = Sentilecto()

    @swagger.operation(notes='<b style="color:red;">SPANISH TEXT ONLY</b><br/>Summarizing.',
                       description='Text summarizing service',
                       responseClass=SummarizingResponse,
                       nickname='summarize',
                       parameters=
                            [
                                {
                                    "name":         "text",
                                    "description":  "Text to be summarized",
                                    "required":     True,
                                    "allowMultiple": False,
                                    "dataType":     "string",
                                    "paramType":    "path"
                                },
                                {
                                    "name":          "api_key",
                                    "description":   "Access token.",
                                    "required":      True,
                                    "allowMultiple": False,
                                    "dataType":      "string",
                                    "paramType":     "path"
                                }
                            ],
                       responseMessages=[
                                {"code": 200, "message": "Text properly rewritten."},
                                {"code": 403, "message": "The authentication token provided is invalid."},
                                {"code": 500, "message": "Bad response"}
                            ]
                      )
    @marshal_with(SummarizingResponse.resource_fields)
    def get(self, text, api_key):
        # api_key = request.headers.get('api_key')
        #print "Rewriting. text:", text

        message = self.validate_token(api_key)
        if len(message) > 0:
            return self.build_response(403, {'type': 'ERROR', 'message': message})

        #print "users_storage"
        users_storage.increase_access_counter(api_key)
        #print "has_type_encoding"

        try:
            #print text
            #print "analysis"
            analysis = self.sentilecto.analyze(text)
            summarized_text = TextSummarizer(analysis).summarize().strip()
            #print "results:", analysis

            analysis_results = \
                {
                    '0-Source-Text'    :  text,
                    '1-Summarized-Text' :  summarized_text
                }
            response_value = analysis_results
            response_code = 200

        except Exception as e:
            response_value = {'type': 'ERROR', 'message': str(e)}
            response_code = 500,
        #print "building response"
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
        #print "returning:", response
        return response

    def validate_token(self, token):
        if not users_storage.is_valid_token(token):
            message = "This token does not belong to a registered user."
        elif users_storage.is_valid_token(token) and users_storage.has_expired(token):
            message = "The token expired (30 days or more than 500 calls)."
        else:
            message = ""

        return message

    def build_response(self, response_code, response_value):
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
