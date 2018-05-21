# -*- coding: utf-8 -*-


from flask_restful import Resource, marshal_with
from flask_restful_swagger import swagger

from src.model.sentilecto import Sentilecto
from src.utils.stringUtils import has_type_encoding
from src.ling.freelingDictionaryParser import FreelingDictionaryParser
from src.utils.webOutputUtils import WebOutputUtils
from models import EntitySentimentReportResponse

import traceback
from usersStorage import users_storage
#from models import EntitiesResponse

__author__ = 'Alexis Balbachan'

class EntitySentimentReport(Resource):
   
    def __init__(self):
        self.sentilecto = Sentilecto()
        
        
    @swagger.operation(notes='<b style="color:red;">SPANISH TEXT ONLY</b><br/>Analyze input text and returns an entity sentiment report. ---- NOTE: This v0.9 is an early release, please expect v1.0 to be released soon. You will find new resources and improved functionality.',
                   description='Natural Language Understanding / Sentiment Analysis service',
                   responseClass=EntitySentimentReportResponse,
                   nickname='get sentiment report',
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
                   responseMessages=[
                            {"code": 200, "message": "Entities properly extracted"},
                            {"code": 403, "message": "The authentication token provided is invalid."},
                            {"code": 500, "message": "Bad response"}
                        ]
                  )    
    
    @marshal_with(EntitySentimentReportResponse.resource_fields)                      
    def get(self, text, api_key):
        #messages1 = "AAAAAAAAAAAAAAAAAAA"
        print "AAAAAAAAAAAAAA"
        messages1 = self.validate_token(api_key)
        if len(messages1) > 0:
            return self.build_response(403, {'type': 'ERROR', 'message': messages1})

        users_storage.increase_access_counter(api_key)    
        if has_type_encoding(text, str, 'UTF-8'):
            text = text.decode('UTF-8')

        try:
            output_utils = WebOutputUtils(None)
            entities_report = []
            analysis = self.sentilecto.analyze(text)

            sentences = analysis["paragraph"].sentences
            text_entities = []
            for sentence in sentences:
            
                for clause in sentence.clauses:
                
                    clause_entities = clause.entities + clause.tacit_entities()
                    clause_entities = filter(lambda entity: not entity.has_attr("implicit") and not entity.has_attr("impersonal"), clause_entities)
                    clause_entities = filter(lambda entity: entity.is_maximal_regarding(clause_entities), clause_entities)

                text_entities.extend(clause_entities)
                
                if clause.relative_entity:
                    text_entities += [clause.relative_entity]
                
            if text_entities:    
        
                referents_data = output_utils.get_referents_data(text_entities)
                
                for referent_data in referents_data:

                    appearing = {}
                    for a_reference in referent_data['refs']:
                        a_reference = str(a_reference)
                        if a_reference in appearing:
                            appearing[a_reference]+=1
                        else:
                            appearing[a_reference]=1
                
                    unique_arr = []    
                    for unique_elem in appearing.iterkeys():
                        unique_arr.append({unique_elem : appearing[unique_elem]})
                
                    occurrences = len(referent_data['refs'])
                    entities_report.append({
                                                "0-Entity-Name": referent_data['rn'], 
                                                "1-Positive-Score": str(referent_data['pos']), 
                                                "2-Negative-Score": str(referent_data['neg']), 
                                                "3-Type": referent_data['sc'], 
                                                "4-Ocurrences": str(occurrences),
                                                "5-Ocurrences-Appearing": unique_arr,
                                           })

            analysis_results = \
                {
                    '0-Paragraph-Text':   analysis["paragraph"].text,
                    '1-Entities-Report':  entities_report
                }
            response_value = analysis_results
            response_code = 200

        except Exception, e:
            print e
            print traceback.format_exc()
            response_value = {'type': 'ERROR', 'message': str(e)}
            response_code = 500,

        response = (
                response_value,
                response_code,
                {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json; '
                    'charset=utf-8'
                }
            )
        #response = {"A":"B"}
        return response
    
    #def validate_token(self, token):
    #    if not users_storage.is_valid_token(token):
    #        message = "This token does not belong to a registered user."
    #    elif users_storage.is_valid_token(token) and users_storage.has_expired(token):
    #        message = "The token expired (30 days or more than 500 calls)."
    #    else:
    #        message = ""
    #    return message
        
        
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




    def options (self, **args):
        return {'Allow': 'GET,PUT,POST,DELETE'}, \
               200, \
               {'Access-Control-Allow-Origin':     '*',
                'Access-Control-Allow-Methods':    'GET,PUT,POST,DELETE',
                'Access-Control-Allow-Headers':    'Content-Type'}      
                

    def validate_token(self, token):
        if not users_storage.is_valid_token(token):
            message = "This token does not belong to a registered user."
        elif users_storage.is_valid_token(token) and users_storage.has_expired(token):
            message = "The token expired (30 days or more than 500 calls)."
        else:
            message = ""

        return message
    
