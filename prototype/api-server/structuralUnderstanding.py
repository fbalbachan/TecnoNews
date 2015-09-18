# -*- coding: utf-8 -*-
from flask_restful_swagger import swagger
import json

from src.model.sentilecto import Sentilecto
from src.utils.stringUtils import has_type_encoding
from models import DeepStructureResponse
from flask_restful import Resource, marshal_with

__author__ = 'Martín Caramés Abente'


class StructuralUnderstanding(Resource):

    sentilecto = Sentilecto()

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


    @swagger.operation(notes='Analyze the text and return a deep insight into its semantic structure. ---- NOTE: This v0.1 is an early release, expect v1.0 coming very soon. In it you\'ll find new resources and improved functionality.',
                       description='Natural Language Understanding service',
                       responseClass=DeepStructureResponse,
                       nickname='get semantic structure',
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
                                {"code": 200, "message": "Structure insights properly generated."},
                                {"code": 500, "message": "Bad response."}
                            ]
                      )
    @marshal_with(DeepStructureResponse.resource_fields)
    def get(self, text):

        slot_names = {'subject':        '0-Subject',
                      'verb':           '1-Verb',
                      'od':             '2-Direct-Object',
                      'equative':       '2-Equative',
                      'regimen':        '2-Phrasal-Verb-Complement',
                      'oi':             '3-Indirect-Object-Experimenter',
                      'instrument_goal': '4-Instrument-Company-Goal-Beneficiary',
                      'adjuncts':       '5-Adjuncts',
                      'time':           '6-Time'}

        if has_type_encoding(text, str, 'UTF-8'):
            text = text.decode('UTF-8')

        try:
            analysis = self.sentilecto.analyze(text)

            sentences = []
            paragraph_sentences = analysis["paragraph"].sentences
            for sentence in paragraph_sentences:

                sentence_data = dict()
                sentence_data['0-Sentence-Text'] = sentence.text
                sentence_data['1-Sentence-Order'] = paragraph_sentences.index(sentence) + 1

                sentence_data['2-Sentence-Clauses'] = []
                for clause in sentence.clauses:
                    deep_structure = dict()
                    clause_data = dict()
                    clause_data["0-Clause-Text"] = str(clause)
                    clause_data["1-Clause-Order"] = str(sentence_data['1-Sentence-Order']) + "." + self.clause_number(clause, sentence)

                    svo_slots = dict()
                    svo_slots["7-Opinionated-Modal-Adverbs"] = ", ".join([str(adverb) for adverb in clause.valuated_adverbs])
                    for structure_name in ['subject', 'verb', 'od', 'equative', 'regimen',
                                           'oi', 'instrument_goal', 'adjuncts', 'time']:
                        svo_slots[slot_names[structure_name]] = self.structure(clause, structure_name)

                    deep_structure['0-Global-Operators'] = [go.klass for go in clause.global_operators]
                    deep_structure['1-SVO-Slots'] = svo_slots

                    clause_data['2-Deep-Structure'] = deep_structure
                    sentence_data['2-Sentence-Clauses'] = sentence_data['2-Sentence-Clauses'] + [clause_data]

                sentences = sentences + [sentence_data]

            analysis_results = \
                {
                    '0-Paragraph-Text':       analysis["paragraph"].text,
                    '1-Entity-Tagged-Text':   analysis["tagged_text"],
                    '2-Sentences':            sentences
                }

            response_value = analysis_results
            response_code = 200

        except Exception, e:
            response_value = {'type': 'ERROR', 'message': str(e)}
            response_code = 500

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

        return response

    def options (self, **args):
        return {'Allow': 'GET,PUT,POST,DELETE'}, \
               200, \
               {'Access-Control-Allow-Origin':     '*',
                'Access-Control-Allow-Methods':    'GET,PUT,POST,DELETE',
                'Access-Control-Allow-Headers':    'Content-Type'}
