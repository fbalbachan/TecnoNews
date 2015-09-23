# -*- coding: utf-8 -*-

import json
import traceback

from flask_restful import Resource, marshal_with
from flask_restful_swagger import swagger
from src.model.sentilecto import Sentilecto
from src.utils.stringUtils import has_type_encoding
from models import DeepStructureResponse
from usersStorage import users_storage

__author__ = 'Martín Caramés Abente'


slot_names = {'subject':        '0-Subject',
              'verb':           '1-Verb',
              'od':             '2-Direct-Object',
              'equative':       '2-Equative',
              'regimen':        '2-Phrasal-Verb-Complement',
              'oi':             '3-Indirect-Object-Experimenter',
              'instrument_goal': '4-Instrument-Company-Goal-Beneficiary',
              'adjuncts':       '5-Adjuncts',
              'time':           '6-Time'}


class StructuralUnderstanding(Resource):

    def __init__(self):
        self.sentilecto = Sentilecto()

    @swagger.operation(notes='Analyze the text and return a deep insight into its semantic structure. ---- NOTE: This v0.9 is an early release, expect v1.0 coming very soon. In it you\'ll find new resources and improved functionality.',
                       description='Natural Language Understanding service',
                       responseClass=DeepStructureResponse,
                       nickname='get semantic structure',
                       parameters=
                           [
                                {
                                    "name":          "text",
                                    "description":   "Text to be Analyzed",
                                    "required":      True,
                                    "allowMultiple": False,
                                    "dataType":      "string",
                                    "paramType":     "path"
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
                                {"code": 200, "message": "Structure insights properly generated."},
                                {"code": 403, "message": "The authentication token provided is invalid."},
                                {"code": 500, "message": "Bad response."}
                            ]
                      )
    @marshal_with(DeepStructureResponse.resource_fields)
    def get(self, text, api_key):
        # api_key = request.headers.get('api_key')

        message = self.validate_token(api_key)
        if len(message) > 0:
            return self.build_response(403, {'type': 'ERROR', 'message': message})

        users_storage.increase_access_counter(api_key)

        api_key = request.headers.get('api_key')
        print "api_key: ", api_key

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

            print "Sentences: ", str(sentences)
            analysis_results = \
                {
                    '0-Paragraph-Text':       analysis["paragraph"].text,
                    '1-Entity-Tagged-Text':   analysis["tagged_text"],
                    '2-Sentences':            sentences
                }

            response_value = analysis_results
            response_code = 200

        except Exception, e:
            print traceback.format_exc()
            response_value = {'type': 'ERROR', 'message': str(e)}
            response_code = 500

        return self.build_response(response_code, response_value)

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
        sentence_data['0-Sentence-Text'] = sentence.text
        sentence_data['1-Sentence-Order'] = index

        sentence_data['2-Sentence-Clauses'] = []
        for clause in sentence.clauses:
            index = str(sentence_data['1-Sentence-Order']) + "." + self.clause_number(clause, sentence)
            clause_data = self.get_clause_data(clause, index)

            sentence_data['2-Sentence-Clauses'] = sentence_data['2-Sentence-Clauses'] + [clause_data]

        sentence_data['3-Sentence-Morphosyntactic-Info'] = self.get_morphosyntactic_info(sentence)

        return sentence_data

    def get_clause_data(self, clause, str_index):

        clause_data = dict()
        clause_data["0-Clause-Text"] = str(clause)
        clause_data["1-Clause-Order"] = str_index

        deep_structure = dict()
        deep_structure['0-Global-Operators'] = [go.klass for go in clause.global_operators]
        deep_structure['1-SVO-Slots'] = self.get_svo_slots(clause)
        clause_data['2-Deep-Structure'] = deep_structure

        return clause_data

    def get_svo_slots(self, clause):
        svo_slots = dict()
        svo_slots["7-Opinionated-Modal-Adverbs"] = ", ".join([str(adverb) for adverb in clause.valuated_adverbs])

        for structure_name in ['subject', 'verb',
                               'od', 'equative', 'regimen',
                               'oi',
                               'instrument_goal', 'adjuncts', 'time']:

            svo_slots[slot_names[structure_name]] = self.structure(clause, structure_name)

        return svo_slots

    def get_morphosyntactic_info(self, sentence):
        morphosyntactic_info = []

        entities = []
        for clause in sentence.clauses:
            for structure in clause.syntactic_structures:
                structure_entities = structure.all_entities()
                if structure_entities:
                    entities = entities + structure.all_entities()

        for entity in entities:

            entity_morphosyntactic_info = dict()
            entity_morphosyntactic_info['0-Entity-Name'] = str(entity)
            entity_morphosyntactic_info['1-Person'] = entity.msi["person"]
            entity_morphosyntactic_info['2-Gender'] = str(entity.msi["gender"])
            entity_morphosyntactic_info['3-Number'] = str(entity.msi["number"])
            entity_morphosyntactic_info['4-Category'] = str(entity.msi["category"])

            if (entity.category() == "noun" or entity.category() == "pronoun") \
               and "animity" in entity.msi:
                entity_morphosyntactic_info['5-Animity'] = entity.msi["animity"].encode("utf-8")

            if entity.is_named_entity():
                classification = str(entity.classification(look_deep=True)).upper()
                entity_morphosyntactic_info['6-Semantic-Classification'] = classification.encode("utf-8")

            if entity_morphosyntactic_info['4-Category'] is "verb":
                entity_morphosyntactic_info['7-Transitivity'] = entity.transitivity.encode("utf-8")
                entity_morphosyntactic_info['8-Sentimental-Script-Class'] = entity.sentimental_script.klass.encode("utf-8")

            morphosyntactic_info = morphosyntactic_info + [entity_morphosyntactic_info]

        return morphosyntactic_info

    def options (self, **args):
        return {'Allow': 'GET,PUT,POST,DELETE'}, \
               200, \
               {'Access-Control-Allow-Origin':     '*',
                'Access-Control-Allow-Methods':    'GET,PUT,POST,DELETE',
                'Access-Control-Allow-Headers':    'Content-Type'}

    def structure(self, clause, name):
        if clause.has_structure(name) and not clause.structure(name).is_empty():
            structure = clause.structure(name)
            if name == "verb":
                return structure.entity().lemma()
            else:
                entities = structure.all_entities()
                infinity = 10000
                entities.sort(key=lambda p_entity: p_entity.token.start() if p_entity.is_explicit() else infinity)
                content = ", ".join([str(entity) for entity in entities])
                return content
        else:
            return ""

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
