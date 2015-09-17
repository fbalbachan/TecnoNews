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

    @swagger.operation(notes='Analyze the text and return a deep insight into its semantic structure.',
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

        if has_type_encoding(text, str, 'UTF-8'):
            text = text.decode('UTF-8')

        try:
            analysis = self.sentilecto.analyze(text)

            sentences = []
            sentence_data = dict()
            for sentence in analysis["paragraph"].sentences:
                sentence_data['clauses'] = []
                clause_structure = dict()
                for clause in sentence.clauses:
                    clause_structure['svo_slots'] = []
                    svo_slot = dict()
                    for structure in clause.syntactic_structures:
                        if structure.name in ['subject', 'verb', 'direct-object', 'equative',
                                              'phrasal-verb-complement', 'indirect-object-experimenter']:
                            svo_slot[structure.name] = str(structure.entities[0])

                        else:  # ['instrument-company-goal-beneficiary', 'adjuncts', 'time']
                            entities = [str(entity) for entity in structure.entities]
                            svo_slot[structure.name] = str(entities)

                        clause_structure['svo_slots'] = clause_structure['svo_slots'] + [svo_slot]

                    clause_structure['entity_tags'] = ""
                    clause_structure['global_operators'] = [""]
                    sentence_data['clauses'] = sentence_data['clauses'] + [clause_structure]

                sentence_data["text"] = sentence.text
                sentences = sentences + [sentence_data]

            analysis_results = \
                {
                    'paragraph':    analysis["paragraph"].text,
                    'sentences':    sentences
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
