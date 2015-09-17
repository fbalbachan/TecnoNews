# -*- coding: utf-8 -*-
from flask_restful_swagger import swagger
import sys
import json

from flask import Flask, redirect, abort, request
from flask_restful import Api
from entityExtraction import EntityExtraction
from structuralUnderstanding import StructuralUnderstanding


reload(sys)
sys.setdefaultencoding("utf-8")

app = Flask(__name__, static_folder='./static')

api = swagger.docs(Api(app),
                   apiVersion='0.1.0',
                   basePath='http://localhost:5000',
                   resourcePath='/v1',
                   produces=["application/json", "text/html"],
                   api_spec_url='/api/spec',
                   description='SentiLecto\'s API')


api.add_resource(EntityExtraction, '/api/v1/entity-extraction/<string:text>')

api.add_resource(StructuralUnderstanding, '/api/v1/deep-structure/<string:text>')


def not_found():
    print "404: Text could not be parsed."
    abort(404, message="Text could not be parsed.")


def bad_request():
    print "500: An error occurred."
    abort(500, message="An error occurred.")


@app.route('/docs')
def docs():
    print "Route docs: redirecting to /static/docs.html"
    return redirect('/static/docs.html')

if __name__ == '__main__':
    print "Running on host 127.0.0.1"
    app.run(host='127.0.0.1', port=5000, debug=True)
