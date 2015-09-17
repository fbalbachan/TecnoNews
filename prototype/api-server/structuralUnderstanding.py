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
	print "1.1"
        if clause.has_structure(name) and not clause.structure(name).is_empty():
	    print "1.2"
            structure = clause.structure(name)
            if name == "verb":
		print "1.3" 
                return structure.entity().lemma()
            else:
		print "1.4"
                entities = structure.all_entities()
		print "entities: ", entities
                infinity = 10000
                entities.sort(key=lambda p_entity: p_entity.token.start() if p_entity.is_explicit() else infinity)
                print "entities: ", entities
		content = ", ".join([str(entity) for entity in entities])
		print "content: ", content
		return content
        else:
	    print "1.5"
            return ""

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
	    print "starting to construct answer."
            for sentence in analysis["paragraph"].sentences:
		sentence_data = dict()
		sentence_data["text"] = sentence.text
                sentence_data['clauses'] = []
                clause_data = dict()
		deep_structure = dict()
                for clause in sentence.clauses:
                    svo_slots = dict()
		    svo_slots["opinionated-modal-adverbs"] = ", ".join([str(adverb) for adverb in clause.valuated_adverbs])
		    print "constructing slot"
                    for structure_name in ['subject', 'verb', 'od', 'equative', 'regimen', 'oi', 'instrument_goal', 'adjuncts', 'time']:
			print "structure: ", structure_name
			slot_names = {'subject': 'subject', 'verb': 'verb', 
				      'od': 'direct-object', 'equative': 'equative', 'regimen': 'phrasal-verb-complement', 
				      'oi': 'indirect-object-experimenter',
				      'instrument_goal': 'instrument-company-goal-beneficiary', 
				      'adjuncts': 'adjuncts',
				      'time': 'time'}
		   
			slot_content = self.structure(clause, structure_name) 
			slot_name = slot_names[structure_name]
			print "slot name: ", slot_name, " - slot_content: ", slot_content
			svo_slots[slot_name] = slot_content

                    deep_structure['svo_slots'] = svo_slots
		    deep_structure['global_operators'] = [""]

		    print "deep_structure: ", str(deep_structure)
                    clause_data['entity_tagged_text'] = ""
		    print "1"
                    clause_data['deep_structure'] = deep_structure
		    print "2"
                    sentence_data['clauses'] = sentence_data['clauses'] + [clause_data]
		    print "3"

		print "Sentence_data: ", str(sentence_data)
                sentences = sentences + [sentence_data]

	    print "Sentences: ", str(sentences)
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
