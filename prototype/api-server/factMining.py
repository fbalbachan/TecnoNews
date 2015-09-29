# -*- coding: utf-8 -*-

import traceback
from _csv import reader
from datetime import datetime, date

from flask_restful_swagger import swagger
from src.model.sentilecto import Sentilecto
from src.utils.stringUtils import has_type_encoding
from flask_restful import Resource, marshal_with, request
from usersStorage import users_storage
from models import FactMiningResponse
from src.utils.configProvider import ConfigProvider
from src.utils.factNormalizer import FactNormalizer
from src.ling.freelingDictionaryParser import FreelingDictionaryParser

__author__ = 'Martín Caramés Abente'


class FactMining(Resource):

    _ontology_parser = FreelingDictionaryParser()
    _ontology = _ontology_parser.get_ontology()

    def __init__(self):
        self.synonyms = self._get_synonyms()
        self.sentilecto = Sentilecto()

    @swagger.operation(notes='Analyze the text and extract named & non-named entities. ---- NOTE: This v0.9 is an early release, expect v1.0 coming very soon. In it you\'ll find new resources and improved functionality.',
                       description='Natural Language Understanding / Sentiment Analysis service',
                       responseClass=FactMiningResponse,
                       nickname='mine facts',
                       parameters=[
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
                       responseMessages=[
                                {"code": 200, "message": "Entities properly extracted"},
                                {"code": 403, "message": "The authentication token provided is invalid."},
                                {"code": 500, "message": "Bad response"}
                            ]
                      )
    @marshal_with(FactMiningResponse.resource_fields)
    def get(self, text, api_key):
        # api_key = request.headers.get('api_key')

        message = self.validate_token(api_key)
        if len(message) > 0:
            return self.build_response(403, {'type': 'ERROR', 'message': message})

        users_storage.increase_access_counter(api_key)

        if has_type_encoding(text, str, 'UTF-8'):
            text = text.decode('UTF-8')

        try:
            analysis = self.sentilecto.analyze(text)

            sentences = []
            paragraph_sentences = analysis["paragraph"].sentences
            index = 0
            for sentence in paragraph_sentences:

                try:
                    index = paragraph_sentences.index(sentence) + 1
                    sentence_data = self.get_sentence_data(sentence, index)
                    sentences = sentences + [sentence_data]

                except Exception as e:
                    print 'Exception while generating sentence information: %s - %s' % (str(index), sentence.text)
                    print traceback.format_exc()

            analysis_results = \
                {
                    '0-Paragraph-Text':     analysis["paragraph"].text,
                    '1-Sentences':          sentences
                }

            response_value = analysis_results
            response_code = 200

            users_storage.update_last_access_date(api_key, datetime.now())
            users_storage.signal_refresh_occasion()

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

    def get_sentence_data(self, sentence, index):
        sentence_data = dict()
        sentence_data['0-Sentence-Order'] = index
        sentence_data['1-Sentence-Text'] = sentence.text

        sentence_data['2-Sentence-Clauses'] = []
        for clause in sentence.clauses:
            print "cl.1"
            clause_data = dict()
            print "cl.2"
            clause_order = str(sentence_data['0-Sentence-Order']) + "." + self.clause_number(clause, sentence)
            print "cl.3"
            clause_data["0-Clause-Order"] = clause_order
            print "cl.4"
            clause_data["1-Clause-Text"] = str(clause)
            print "cl.5"
            fact = FactNormalizer(clause, FactMining._ontology, self.synonyms).fact()
            print "cl.6"
            clause_data["2-Clause-Normalized-Fact"] = str(fact)
            print "cl.7"
            sentence_data['2-Sentence-Clauses'] = sentence_data['2-Sentence-Clauses'] + [clause_data]
            print "cl.8"

        print "cl.9"
        return sentence_data

    def clause_number(self, clause, sentence):
        number_string = ""
        while not clause.is_root():
            father = clause.father
            number = father.children.index(clause) + 1
            number_string = "." + str(number) + number_string
            clause = father

        number = sentence.clauses.index(clause) + 1
        number_string = str(number) + number_string

        return number_string

    def _get_synonyms(self):
        return self._get_replacements_from_csv("synonyms")

    def _get_replacements_from_csv(self, resource):
        # Warning, it is a dict, it doesn't work for multiple replacements for the same word.
        replacements = {}
        config = ConfigProvider()
        replacements_filename = config.get("resources", resource)
        for line in reader(open(replacements_filename, 'r')):
            replacements[line[0]] = line[1]
            replacements[line[1]] = line[0]
        return replacements

    def options (self, **args):
        return {'Allow': 'GET,PUT,POST,DELETE'}, \
               200, \
               {'Access-Control-Allow-Origin':     '*',
                'Access-Control-Allow-Methods':    'GET,PUT,POST,DELETE',
                'Access-Control-Allow-Headers':    'Content-Type'}
