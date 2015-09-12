# -*- coding: utf-8 -*-
from flask import Flask, redirect, abort
from flask_restful import Api, Resource, reqparse, marshal_with
from flask_restful_swagger import swagger
from src.model.sentilecto import Sentilecto
from src.utils.stringUtils import has_type_encoding
from models import TextAnalyze, Analyzer


import sys
import json

reload(sys)
sys.setdefaultencoding("utf-8")

app = Flask(__name__, static_folder='./static')

api = swagger.docs(Api(app),
                   apiVersion='0.1.0',
                   basePath='http://localhost:5000',
                   resourcePath='/v1',
                   produces=["application/json", "text/html"],
                   api_spec_url='/api/spec',
                   description='SentiLite API')


def NotFound():
    print "404: Text could not be parsed."
    abort(404, message="Text could not be parsed.")


def BadRequest():
    print "500: An error occurred."
    abort(500, message="An error occurred.")

print "Building req parser."
#parser = reqparse.RequestParser()

print "Adding argument."
#parser.add_argument('text', type=str)


class TextAnalysis(Resource):

    sentilecto = Sentilecto()

    @swagger.operation(notes='Analyze the text you get',
                       description='Text Analyze service',
                       responseClass=Analyzer.__name__,
                       nickname='get analysis',
                       parameters=[{"name":         "text",
                                    "description":  "Text to be Analyzed",
                                    "required":     True,
                                    "allowMultiple": False,
                                    "dataType":     "string",
                                    "paramType":    "path"}],
                       responseMessages=[{"code": 200, "message": "Facts extracted properly"},
                                         {"code": 500, "message": "Bad response"}]
                      )
#    @marshal_with(TextAnalyze.resource_fields)
    def get(self, text):
        #args = parser.parse_args()
        #print "args text: ", args['text']

        print "text: ", text

        if has_type_encoding('text', str, 'UTF-8'):
            text = text.decode('UTF-8')
            print "str - utf-8 - text: ", text

        elif has_type_encoding(text, unicode):
            print "unicode - text: ", text
            text = unicode(text, 'utf-8', errors='ignore')

        else: # has_type_encoding(args['text'], unicode)
            print "unicode - text: ", text

        try:
            print "Analyzing text: ", text
            analysis = self.sentilecto.analyze(text)
            print "analysis: ", analysis

            analysis_results = analysis.to_dict()
            print "analysis_results: ", analysis_results

            analysis_results_unicode = unicode(str(analysis_results))
            print "analysis_results_unicode: ", analysis_results_unicode

            return app.make_response((analysis_results_unicode,
                                      200,
                                      {'Access-Control-Allow-Origin': '*',
                                       'Content-Type': 'application/json; '
                                       'charset=utf-8'}
                                     ))
        except Exception, e:
            print str(e), " - 'Access-Control-Allow-Origin'"
            return app.make_response((str({'type': 'ERROR', 'message': str(e)}),
                                      500,
                                      {'Access-Control-Allow-Origin': '*',
                                       'Content-Type': 'application/json; '
                                       'charset=utf-8'}))


    def options (self, **args):
        return {'Allow': 'GET,PUT,POST,DELETE'}, 200, \
               {'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,PUT,POST,DELETE',
                'Access-Control-Allow-Headers': 'Content-Type'}

api.add_resource(TextAnalysis, '/api/v1/text/<string:text>')


@app.route('/docs')
def docs():
    print "Route docs: redirecting to /static/docs.html"
    return redirect('/static/docs.html')

if __name__ == '__main__':
    print "Running on host 0.0.0.0"
    app.run(host='0.0.0.0', debug = True)
