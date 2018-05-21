# -*- coding: utf-8 -*-

from flask_restful_swagger import swagger
import traceback

from src.model.sentilecto import Sentilecto
from src.utils.stringUtils import has_type_encoding
from models import SentimentAnalysisResponse
from flask_restful import Resource, marshal_with
from usersStorage import users_storage
import requests
import json
import urllib

__author__ = 'Alexis Balbachan'


class SentimentAnalysisPT(Resource):

    def __init__(self):
        self.sentilecto = Sentilecto()

    @swagger.operation(notes='<b style="color:red;">PORTUGUESE TEXT ONLY</b><br/>Analyzes input utf-8 encoded text and returns extensive and fine-grained sentiment scores for each entity. ---- NOTE: This v0.9 is an early release, please expect v1.0 to be released soon. You will find new resources and improved functionality.',
                       description='Natural Language Understanding service',
                       responseClass=SentimentAnalysisResponse,
                       nickname='get sentiment analysis',
                       parameters=[
                                {
                                    "name":         "text",
                                    "description":  "Text to be Analyzed",
                                    "required":     True,
                                    "allowMultiple": False,
                                    "dataType":     "string",
                                    "paramType":    "path"
                                }, {
                                    "name":          "api_key",
                                    "description":   "Access token.",
                                    "required":      True,
                                    "allowMultiple": False,
                                    "dataType":      "string",
                                    "paramType":     "path"
                                }],
                       responseMessages=[{"code": 200, "message": "Sentiment details generated properly."},
                                         {"code": 403, "message": "The authentication token provided is invalid."},
                                         {"code": 500, "message": "Bad response."}
                                         ]
                       )
    # @marshal_with(SentimentAnalysisResponse.resource_fields)
    def get(self, text, api_key):
        # url = "http://127.0.0.1:5500/api/v0.9/sentiment-analysis/" + urllib.quote_plus(text.encode("utf-8")) + "/" + api_key
        url = "http://127.0.0.1:5500/api/v0.9/sentiment-analysis/" + test.replace('?', ';;::;;::') + "/" + urllib.quote(api_key, safe='')
        req = requests.get(url)
        text = req.text
        status = req.status_code
        response = \
            (
                json.loads(text),
                status,
                {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json; '
                    'charset=utf-8'
                }
            )

        return response

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

    def validate_token(self, token):
        if not users_storage.is_valid_token(token):
            message = "This token does not belong to a registered user."
        elif users_storage.is_valid_token(token) and users_storage.has_expired(token):
            message = "The token expired (30 days or more than 500 calls)."
        else:
            message = ""

        return message

    def options(self, **args):
        return {'Allow': 'GET,PUT,POST,DELETE'}, \
            200, \
               {'Access-Control-Allow-Origin':     '*',
                'Access-Control-Allow-Methods':    'GET,PUT,POST,DELETE',
                'Access-Control-Allow-Headers':    'Content-Type'}
