# -*- coding: utf-8 -*-

from flask_restful_swagger import swagger
#import json
import traceback

from src.model.sentilecto import Sentilecto
from src.utils.stringUtils import has_type_encoding
from models import SentimentAnalysisResponse
from flask_restful import Resource, marshal_with

__author__ = 'Martín Caramés Abente'


class SentimentAnalysis(Resource):

    sentilecto = Sentilecto()

    @swagger.operation(notes='Analyze the text and return extensive and fine-grained sentiment scores for every structure. ---- NOTE: This v0.9 is an early release, expect v1.0 coming very soon. In it you\'ll find new resources and improved functionality.',
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
                                }
                           ],
                       responseMessages=
                            [
                                {"code": 200, "message": "Sentiment details generated properly."},
                                {"code": 500, "message": "Bad response."}
                            ]
                      )
    @marshal_with(SentimentAnalysisResponse.resource_fields)
    def get(self, text):
        print "1"
        if has_type_encoding(text, str, 'UTF-8'):
            text = text.decode('UTF-8')

        try:
            print "2"
            analysis = self.sentilecto.analyze(text)
            print "3"
            paragraph = analysis["paragraph"]
            print "4"
            sentiment_summary = analysis["summary"]
            print "5"

            sentences_data = []
            for sentence in analysis["paragraph"].sentences:
                print "6"
                sentence_data = dict()
                sentence_data["0-Sentence-Text"] = sentence.text
                print "7"

                score = dict()
                score["0-Positive-Score"] = sentiment_summary[sentence]['positive']
                score["1-Negative-Score"] = sentiment_summary[sentence]['negative']
                sentence_data["1-Sentence-Sentiment-Score"] = score
                print "8"

                clauses_data = []
                for clause in sentence.clauses:
                    print "9"
                    clause_data = dict()
                    clause_data['0-Clause-Text'] = str(clause)
                    print "10"

                    score = dict()
                    score["0-Positive-Score"] = sentiment_summary[clause]['positive']
                    print "11"
                    score["1-Negative-Score"] = sentiment_summary[clause]['negative']
                    print "12"
                    clause_data['1-Clause-Sentiment-Score'] = score
                    print "13"

                    entities_data = []
                    for entity in clause.all_entities():
                        print "14"
                        entity_data = dict()
                        entity_data['0-Entity-Text'] = str(entity)

                        score = dict()
                        print "15"
                        score["0-Positive-Score"] = entity.sentimental_value.value[0]
                        print "16"
                        score["1-Negative-Score"] = entity.sentimental_value.value[1]
                        print "17"
                        entity_data['1-Entity-Sentiment-Score'] = score
                        print "18"

                        entities_data = entities_data + [entity_data]
                        print "19"

                    print "20"
                    clause_data['2-Entities'] = entities_data
                    print "21"

                    clauses_data = clauses_data + [clause_data]
                    print "22"

                print "23"
                sentence_data["2-Clauses"] = clauses_data
                print "24"

                sentences_data = sentences_data + [sentence_data]
                print "25"

            score = dict()
            score["0-Positive-Score"] = sentiment_summary[paragraph]['positive']
            score["1-Negative-Score"] = sentiment_summary[paragraph]['negative']
            print "26"
            analysis_results = \
                {
                    '0-Paragraph-Text':             analysis["paragraph"].text,
                    '1-Paragraph-Sentiment-Score':  score,
                    '2-Sentences':                  sentences_data
                }

            print "27"
            response_value = analysis_results
            response_code = 200
            print "28"

        except Exception, e:
            print traceback.format_exc()
            response_value = {'type': 'ERROR', 'message': str(e)}
            response_code = 500

        print "29"
        # json.dumps(@marshal_with(response_value, StructureResponse.resource_fields))
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
        print "30"

        return response

    def options (self, **args):
        return {'Allow': 'GET,PUT,POST,DELETE'}, \
               200, \
               {'Access-Control-Allow-Origin':     '*',
                'Access-Control-Allow-Methods':    'GET,PUT,POST,DELETE',
                'Access-Control-Allow-Headers':    'Content-Type'}
