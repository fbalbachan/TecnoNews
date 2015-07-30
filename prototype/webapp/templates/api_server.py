# from flask import Flask
# from flask.ext.restful import  Api
# from flask_restful_swagger import swagger

# app = Flask(__name__)


# class TextAnalysis(Resource):
#    @swagger.operation(
#        notes='Analyze the text you get',
#        responseClass=None,
#        nickname='get analysis',
#        parameters=[
#             {
#               "name": "body",
#               "description": "Text to be Analyzed",
#               "required": True,
#               "allowMultiple": False,
#               "dataType": None,
#               "paramType": "body"
#             }
#           ],
#         responseMessages=[
#             {
#               "code": 200,
#               "message": "Facts extracted properly"
#             },
#             {
#               "code": 500,
#               "message": "Bad response"
#             }
#           ]
#         )
# 	def get(self, id):
# 		pass
