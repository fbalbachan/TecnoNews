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
import requests
import json

__author__ = 'Alexis Balbachan'


class FactMiningPT(Resource):

    _ontology_parser = FreelingDictionaryParser()
    _ontology = _ontology_parser.get_ontology()

    def __init__(self):
        self.synonyms = self._get_synonyms()
        self.sentilecto = Sentilecto()

    @swagger.operation(notes='<b style="color:red;">PORTUGUESE TEXT ONLY</b><br/>Analyze the text extracting named entities and the facts those entities are involved in. '
                             'Fact: is a triad S.V.O., Subject-Verb-Object, meaning: an agent (syntactic subject), '
                             'an action (verb) and the object over which rests the action. The results is structured as '
                             'follows: ---- NOTE: This v0.9 is an early release, please expect v1.0 to be released soon. You will find new resources and improved functionality. ',
                       description='Natural Language Understanding / Fact Mining',
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
    #@marshal_with(FactMiningResponse.resource_fields)
    def get(self, text, api_key):
        url    = "http://127.0.0.1:5500/api/v0.9/fact-mining/" + text.replace("?", ";;::;;::") + "/" + api_key
        req    = requests.get(url)
        text   = req.text
        status = req.status_code
        response = \
            (
                json.loads(text) ,
                status ,
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
            clause_data = self.get_clause_data(clause, sentence, sentence_data)
            sentence_data['2-Sentence-Clauses'] = sentence_data['2-Sentence-Clauses'] + [clause_data]

        return sentence_data

    def get_clause_data(self, clause, sentence, sentence_data):
        clause_data = dict()
        clause_order = str(sentence_data['0-Sentence-Order']) + "." + self.clause_number(clause, sentence)
        clause_data["0-Clause-Order"] = clause_order
        clause_data["1-Clause-Text"] = str(clause)
        clause_data["2-Clause-Normalized-Fact"] = self.get_normalized_fact(clause)
        return clause_data

    def get_normalized_fact(self, clause):
        fact = FactNormalizer(clause, FactMining._ontology).fact()
        real_or_not = FactNormalizer.fact_real_or_not(clause)
        return str(fact) + " " + str(real_or_not)

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
        for line in reader(open(replacements_filename, 'r', encoding="utf-8")):
            replacements[line[0]] = line[1]
            replacements[line[1]] = line[0]
        return replacements

    def options (self, **args):
        return {'Allow': 'GET,PUT,POST,DELETE'}, \
               200, \
               {'Access-Control-Allow-Origin':     '*',
                'Access-Control-Allow-Methods':    'GET,PUT,POST,DELETE',
                'Access-Control-Allow-Headers':    'Content-Type'}
