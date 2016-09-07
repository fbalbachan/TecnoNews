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
from src.utils.fact_compare import FactCompare
from src.ling.freelingDictionaryParser import FreelingDictionaryParser

__author__ = 'Alexis Balbachan'


class FactMining(Resource):

    _ontology_parser = FreelingDictionaryParser()
    _ontology = _ontology_parser.get_ontology()

    def __init__(self):
        self.synonyms = self._get_synonyms()
        self.sentilecto = Sentilecto()

    @swagger.operation(notes='<b style="color:red;">SPANISH TEXT ONLY</b><br/>Analyze the text extracting named entities and the facts those entities are involved in. '
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
                    sentence_data = self.get_sentence_data(sentence, index, paragraph_sentences)
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

    def get_sentence_data(self, sentence, index, paragraph_sentences):
        sentence_data = dict()
        sentence_data['0-Sentence-Order'] = index
        sentence_data['1-Sentence-Text'] = sentence.text

        sentence_data['2-Sentence-Clauses'] = []
        for clause in sentence.clauses:
            clause_data = self.get_clause_data(clause, sentence, sentence_data, paragraph_sentences)
            sentence_data['2-Sentence-Clauses'] = sentence_data['2-Sentence-Clauses'] + [clause_data]

        return sentence_data

    def get_clause_data(self, clause, sentence, paragraph_sentences):
        clause_data = dict()
        clause_order = str(sentence_data['0-Sentence-Order']) + "." + self.clause_number(clause, sentence)
        clause_data["0-Clause-Order"] = clause_order
        clause_data["1-Clause-Text"] = str(clause)
        clause_data["2-Clause-Normalized-Fact"] = self.get_normalized_fact(clause)
        clause_data["3-Clause-Comparison"] = []
        
        sentence_index = 0
        for a_sentence in paragraph_sentences:
            for a_clause in a_sentence.clauses:
                if a_clause == clause:
                    continue
                
                score = FactCompare(clause, a_clause).compare()
                if score == 0:
                    score = int(score)
                    
                clause_data["3-Clause-Comparison"].append({"0-Clause-Order": str(sentence_index)+"."+self.clause_number(a_clause, sentence). "1-Score": str(score)})
                
            sentence_index += 1
                    
                
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
