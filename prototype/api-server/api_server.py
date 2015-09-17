# -*- coding: utf-8 -*-
from flask import Flask, redirect, abort, request
from flask_restful import Api, Resource, reqparse, marshal_with
from flask_restful_swagger import swagger
from src.model.sentilecto import Sentilecto
from src.utils.stringUtils import has_type_encoding
from models import TextAnalyze, Analyzer
import os

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


def write_pid_file():
    pid = str(os.getpid())
    pid_file = './sentilecto-api.pid'
    file(pid_file, 'w').write(pid)


def not_found():
    print "404: Text could not be parsed."
    abort(404, message="Text could not be parsed.")


def bad_request():
    print "500: An error occurred."
    abort(500, message="An error occurred.")


class TextAnalysis(Resource):

    sentilecto = Sentilecto()

    @swagger.operation(notes='Analyze the text you get',
                       description='Text Analyze service',
                       responseClass=Analyzer,
                       nickname='get analysis',
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
                                {"code": 200, "message": "Facts extracted properly"},
                                {"code": 500, "message": "Bad response"}
                            ]
                      )
    @marshal_with(Analyzer.resource_fields)
    def get(self, text):

        if has_type_encoding(text, str, 'UTF-8'):
            text = text.decode('UTF-8')

        try:
            analysis = self.sentilecto.analyze(text)

            analysis_results = {'paragraph': analysis["paragraph"].text,
                                'sentences': [sentence.text for sentence in analysis["paragraph"].sentences],
                                'tagged_text': analysis["tagged_text"]}

            response = (
                            analysis_results,
                            200,
                            {
                                'Access-Control-Allow-Origin': '*',
                                'Content-Type': 'application/json; '
                                'charset=utf-8'
                            }
                       )

        except Exception, e:
            response = (
                            {'type': 'ERROR', 'message': str(e)},
                            500,
                            {
                                'Access-Control-Allow-Origin': '*',
                                'Content-Type': 'application/json; '
                                'charset=utf-8'
                            }
                       )

        return response

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
    print "Running on host 127.0.0.1"

    write_pid_file()
    app.run(host='127.0.0.1', port=5000, debug=True)

