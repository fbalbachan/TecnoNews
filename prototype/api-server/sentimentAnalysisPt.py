# -*- coding: utf-8 -*-

from flask_restful_swagger import swagger
import traceback

from src.model.sentilecto import Sentilecto
from src.utils.stringUtils import has_type_encoding
from models import SentimentAnalysisResponse
from flask_restful import Resource, marshal_with
from usersStorage import users_storage
import requests

__author__ = 'Alexis Balbachan'


class SentimentAnalysisPT(Resource):

    def __init__(self):
        self.sentilecto = Sentilecto()

    @swagger.operation(notes='Analyzes input utf-8 encoded text and returns extensive and fine-grained sentiment scores for each entity. ---- NOTE: This v0.9 is an early release, please expect v1.0 to be released soon. You will find new resources and improved functionality.',
                       description='Natural Language Understanding service',
                       responseClass=SentimentAnalysisResponse,
                       nickname='get sentiment analysis',
                       parameters=
                            [
                                {
                                    "name":         "text",
                                    "description":  "Text to be Analyzed",
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
                       responseMessages=
                            [
                                {"code": 200, "message": "Sentiment details generated properly."},
                                {"code": 403, "message": "The authentication token provided is invalid."},
                                {"code": 500, "message": "Bad response."}
                            ]
                      )
    @marshal_with(SentimentAnalysisResponse.resource_fields)
    def get(self, text, api_key):
        
        req = requests.get("http://127.0.0.1:5500/api/spec.json", stream = True)
        
        response = \
            (
                stream_with_context(req.iter_content()),
                response_code,
                {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json; '
                    'charset=utf-8'
                }
            )

        return response

        
        # api_key = request.headers.get('api_key')

        message = self.validate_token(api_key)
        if len(message) > 0:
            return self.build_response(403, {'type': 'ERROR', 'message': message})

        users_storage.increase_access_counter(api_key)

        if has_type_encoding(text, str, 'UTF-8'):
            text = text.decode('UTF-8')

        try:
            analysis = self.sentilecto.analyze(text)
            paragraph = analysis["paragraph"]
            sentiment_summary = analysis["summary"]

            sentences_data = []
            for sentence in analysis["paragraph"].sentences:
                sentence_data = dict()
                sentence_data["0-Sentence-Text"] = sentence.text

                score = dict()
                score["0-Positive-Score"] = sentiment_summary[sentence]['positive']
                score["1-Negative-Score"] = sentiment_summary[sentence]['negative']
                sentence_data["1-Sentence-Sentiment-Score"] = score

                clauses_data = []
                for clause in sentence.clauses:
                    clause_data = dict()
                    clause_data['0-Clause-Text'] = str(clause)

                    score = dict()
                    score["0-Positive-Score"] = sentiment_summary[clause]['positive']
                    score["1-Negative-Score"] = sentiment_summary[clause]['negative']
                    clause_data['1-Clause-Sentiment-Score'] = score

                    entities_data = []
                    for entity in clause.all_entities():
                        entity_data = dict()
                        entity_data['0-Entity-Text'] = str(entity)

                        score = dict()
                        score["0-Positive-Score"] = entity.sentimental_value.value[0]
                        score["1-Negative-Score"] = entity.sentimental_value.value[1]
                        entity_data['1-Entity-Sentiment-Score'] = score

                        entities_data = entities_data + [entity_data]

                    clause_data['2-Entities'] = entities_data

                    clauses_data = clauses_data + [clause_data]

                sentence_data["2-Clauses"] = clauses_data

                sentences_data = sentences_data + [sentence_data]

            score = dict()
            score["0-Positive-Score"] = sentiment_summary[paragraph]['positive']
            score["1-Negative-Score"] = sentiment_summary[paragraph]['negative']

            analysis_results = \
                {
                    '0-Paragraph-Text':             analysis["paragraph"].text,
                    '1-Overall-Sentiment-Score':  score,
                    '2-Sentences':                  sentences_data
                }

            response_value = analysis_results
            response_code = 200

        except Exception, e:
            print traceback.format_exc()
            response_value = {'type': 'ERROR', 'message': str(e)}
            response_code = 500

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

    def options (self, **args):
        return {'Allow': 'GET,PUT,POST,DELETE'}, \
               200, \
               {'Access-Control-Allow-Origin':     '*',
                'Access-Control-Allow-Methods':    'GET,PUT,POST,DELETE',
                'Access-Control-Allow-Headers':    'Content-Type'}
