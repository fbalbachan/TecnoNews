# -*- coding: utf-8 -*-

import os, sys, json

from flask import Flask, redirect, abort
from flask_restful import Api
from flask_restful_swagger import swagger
from entityExtraction import EntityExtraction
from structuralUnderstanding import StructuralUnderstanding
from sentimentAnalysis import SentimentAnalysis
from factMining import FactMining


reload(sys)
sys.setdefaultencoding("utf-8")

api_root_path = "/api"
resource_path = '/v0.9'
base_path = api_root_path + resource_path

app = Flask(__name__, static_folder='./static')

api = swagger.docs(Api(app),
                   apiVersion='0.9.0',
                   basePath='http://localhost:5000',
                   resourcePath=resource_path,
                   produces=["application/json", "text/html"],
                   api_spec_url='/api/spec',
                   description='SentiLecto\'s API')

api.add_resource(SentimentAnalysis, base_path + '/sentiment-analysis/<string:text>/<string:api_key>')

api.add_resource(StructuralUnderstanding, base_path + '/deep-structure/<string:text>/<string:api_key>')

api.add_resource(EntityExtraction, base_path + '/entity-extraction/<string:text>/<string:api_key>')

api.add_resource(FactMining, base_path + '/fact-mining/<string:text>/<string:api_key>')


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


@app.route('/docs')
def docs():
    print "Route docs: redirecting to /static/docs.html"
    return redirect('/static/docs.html')

if __name__ == '__main__':
    print "Running on host 127.0.0.1"

    write_pid_file()
    app.run(host='127.0.0.1', port=5000, debug=True)

