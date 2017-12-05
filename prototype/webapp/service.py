#!/usr/bin/python
# -*- coding: utf-8 -*-

from StringIO import StringIO
import logging
import os
import sys
from threading import Timer
import time
from traceback import format_exc
import subprocess
import random
import codecs

import web
from skimpyGimpy import skimpyAPI

from src.model.contentRewriterAndGenerator import ContentRewriterAndGenerator
from src.model.sentilecto import Sentilecto
from src.utils.webOutputUtils import WebOutputUtils
from src.utils.configProvider import ConfigProvider
from src.ling.freelingDictionaryParser import FreelingDictionaryParser
from src.utils.freelingLanguageDetectorClient import FreelingLanguageDetectorClient

from src.utils.textSummarizer import TextSummarizer
from src.utils.quoteFinder import QuoteFinder

from BeautifulSoup import BeautifulSoup
import urllib2
import re

from src.utils.apiConnector import ApiConnector


request_id = 0
request_data = {}
captchas_by_request = {}
cleanup_timer = None

config = ConfigProvider()
debug_mode = (config.get("debug", "debug") == "True")
ontology = FreelingDictionaryParser.get_ontology()
freeling_language_detector = FreelingLanguageDetectorClient()


def parse_url(url):
    try:
        page = urllib2.urlopen(url)

        soup = BeautifulSoup(page.read())
        texts = soup.findAll("p")
    except Exception:
        texts = []

    textParagraphs = []
    for node in texts:
        temp = ''.join(node.findAll(text=True))
        if re.match(".*[.]$", temp):
            textParagraphs.append(temp)

    return "\n".join(textParagraphs)


def financial_result(analysis):
    import json
    crimes = ['corrup', 'droga', 'narco', 'estupefac', 'econ', 'terroris', 'peculado', 'enriqueci', 'estafa', 'fraud', 'quiebra', 'acreedor', 'deud', 'embarg', 'contraband', 'lavad', 'soborn', 'evadir', 'evasión', 'evadido', 'cohecho', 'coim']
    infinitive_blacklist = ['escribir']
    oraciones = {}
    for a_sentence in analysis["paragraph"].sentences:
        oraciones[str(a_sentence)] = []
        # CONTROL FOR SMART
        sentence_disabled = False
        smart_partial_result = []
        for a_clause in a_sentence.clauses:
            '''
            # CONCEPT DEMO FOR DETECTING S.M.A.R.T. OBJETIVES IN R.R.H.H.
            # CONDITION 1 FOR INFINITIVES
            if a_clause.global_operators and any(a_go.klass != 'volitive' for a_go in a_clause.global_operators):
                sentence_disabled = True
                smart_partial_result = []

            if a_clause.verb and a_clause.verb.msi['time'] != 'presente':
                sentence_disabled = True
                # smart_partial_result = []

            if a_clause.node.nodes_with_labels('infinitiu') and (not a_clause.global_operators or 'volitive' in [a_go.klass for a_go in a_clause.global_operators][0]):
                infinitiu_node = a_clause.node.nodes_with_labels('infinitiu')[0]
                infinitive_verb = infinitiu_node.leaves()[0]

                is_volitive = len(a_clause.global_operators) > 0 and 'volitive' in [a_go.klass for a_go in a_clause.global_operators][0]

                path_to_root = [a_node.label for a_node in infinitiu_node.path_to_root()]

                if infinitive_verb.lemma in infinitive_blacklist or 'grup-sp-inf' in path_to_root or sentence_disabled or (not is_volitive and a_clause.verb and infinitive_verb.lemma == a_clause.verb.lemma()):
                    pass
                elif not infinitiu_node.father.children[0].is_leaf() and infinitiu_node.father.children[0].label == 'neg':
                    pass
                else:
                    smart_partial_result.append({'SMART Objective': str(a_sentence), 'Target': str(a_clause), 'Condition': 'Lema "Objetivo" implícito'})

            # CONDITION 2 FOR LEMMA OBJETIVO
            if any(a_leaf.lemma in ["objetivo", 'meta'] for a_leaf in a_clause.proper_tree().leaves()) and a_clause.is_fact():
                if a_clause.verb and a_clause.verb.msi["time"] not in ["pasado", "imperfecto"] or a_clause.node.nodes_with_labels('infinitiu'):
                    oraciones[str(a_sentence)].append({'SMART Objective': str(a_sentence), 'Target': str(a_clause), 'Condition': 'Lema "Objetivo" explícito'})
            '''
            # SEPARATOR -------------------------------
            if a_clause.verb is not None:
                if a_clause.verb.lemma() in ['estafar', 'defraudar', 'quebrar', 'evadir', 'sobornar', 'coimear']:
                    if a_clause.has_structure('subject') and a_clause.structure('subject').entity().referent.semantic_classification() in ['person', 'organization']:
                        oraciones[str(a_sentence)].append({'Suspect': str(a_clause.structure('subject').entity().referent.designated_ref()), 'Condition': 'Agent'})
                        # print "DETECTA CONDICION 1"

                if a_clause.verb.lemma() in ['investigar', 'denunciar', 'condenar', 'acusar', 'procesar', 'implicar', 'involucrar', 'sentenciar']:
                    if a_clause.has_structure('od') and a_clause.structure('od').entity().referent.semantic_classification() in ['person', 'organization']:
                        for an_entity in a_clause.structure('adjuncts').all_entities():
                            if any(a_word in an_entity.referent.designated_ref().lexical_form for a_word in crimes):
                                oraciones[str(a_sentence)].append({'Suspect': str(a_clause.structure('od').entity().referent.designated_ref()), 'Condition': 'Accused'})
                                # print "DETECTA CONDICION 2"
                                break

                if a_clause.verb.lemma() in ['realizar', 'hacer', 'cometer', 'perpetrar', 'llevar_a_cabo', 'llevar_adelante', 'organizar', 'planear', 'implementar', 'articular', 'tener']:
                    if a_clause.has_structure('subject') and a_clause.structure('subject').entity().referent.semantic_classification() in ['person', 'organization']:
                        for a_structure in [structure.name for structure in a_clause.syntactic_structures]:
                            if a_clause.has_structure(a_structure):
                                for an_entity in a_clause.structure(a_structure).all_entities():
                                    if any(a_word in an_entity.referent.designated_ref().lexical_form for a_word in crimes):
                                        oraciones[str(a_sentence)].append({'Suspect': str(a_clause.structure('subject').entity().referent.designated_ref()), 'Condition': 'Explicit'})
                                        # print "DETECTA CONDICION 3"
                                        break

                if a_clause.verb.lemma() in ['estar']:
                    if a_clause.has_structure('subject') and a_clause.structure('subject').entity().referent.semantic_classification() in ['person', 'organization'] and any(a_false_entity.lemma in ['investigar', 'denunciar', 'condenar', 'acusar', 'procesar', 'implicar', 'involucrar', 'sentenciar'] for a_false_entity in a_clause.false_entities):
                        for an_entity in (a_clause.structure('adjuncts').all_entities() + a_clause.structure('equative').all_entities()):
                            if any(a_word in an_entity.referent.designated_ref().lexical_form for a_word in crimes):
                                oraciones[str(a_sentence)].append({'Suspect': str(a_clause.structure('subject').entity().referent.designated_ref()), 'Condition': 'Justice State'})
                                # print "DETECTA CONDICION 5"
                                break

            for a_structure in [structure.name for structure in a_clause.syntactic_structures]:
                if a_clause.has_structure(a_structure):
                    for an_entity in a_clause.structure(a_structure).all_entities():
                        referent_entity = an_entity.referent.designated_ref()
                        if referent_entity.is_explicit() and referent_entity.kernel is not None and any(a_word in referent_entity.kernel.lexical_form for a_word in crimes):
                            for a_nested_entity in referent_entity.get_nested_entities():
                                if a_nested_entity.referent.semantic_classification() in ['person', 'organization'] and a_nested_entity.is_subordinated_with_preposition('de'):
                                    oraciones[str(a_sentence)].append({'Suspect': str(a_nested_entity), 'Condition': 'Inferred'})
                                    # print "DETECTA CONDICION 4"
        oraciones[str(a_sentence)].extend(smart_partial_result)
    output = ""
    for a_sentence in oraciones:
        if len(oraciones[a_sentence]) > 0:
            output += "\n" + str(a_sentence)
        for a_condition in oraciones[a_sentence]:
            output += "\n-" + json.dumps(a_condition) + "\n"

    return output


def generate_captcha(req_id):
    captcha_key = os.urandom(2).encode("hex")
    request_data[req_id] = {"captcha": captcha_key,
                            "start": time.time()}

    generator = skimpyAPI.Png(captcha_key)
    generator.data(captcha_filename_for(req_id))


def captcha_filename_for(req_id):
    return "static/captcha/captcha_" + str(req_id) + ".png"


def cleanup_sessions():
    expired = []
    for req_id in request_data:  # @ReservedAssignment
        start = request_data[req_id]["start"]
        elapsed_minutes = (time.time() - start) / 60
        if elapsed_minutes > 5:
            expired.append(req_id)

    for req_id in expired:
        cleanup_session(req_id)  # @ReservedAssignment

    cleanup_timer.run()


def cleanup_session(p_request_id):
    del request_data[p_request_id]
    os.remove(captcha_filename_for(p_request_id))


def detect_language(input_text):
    result = freeling_language_detector.parse(input_text.replace('\n', ' '))
    if result[0] == u'':
        return None
    else:
        return result[0]


def get_input_text():
    try:
        web_input = web.input()
        # x = web.input(datafile={})
        x = web.input(myfile={})
        try:
            file_contents = x['myfile'].file.read()  # Or use a file(-like) object
        except:
            file_contents = ""

        if file_contents != "":
            text = unicode(file_contents, "utf-8")
        else:
            text = web_input.text if ("url-input" not in web_input or web_input["url-input"] == "") else parse_url(web_input["url-input"])

        return text

    except Exception:
        print format_exc()

        if debug_mode:
            web.template.render().exception(format_exc(), "")

        return ""




def analyze(debug_output=False):

    try:
        #web_input = web.input()
        ## x = web.input(datafile={})
        #x = web.input(myfile={})
        #try:
        #    file_contents = x['myfile'].file.read() # Or use a file(-like) object
        #except:
        #    file_contents = ""

        #if file_contents != "":
        #    text = file_contents
        #else:
        #    text = web_input.text if ("url-input" not in web_input or web_input["url-input"] == "") else parse_url(web_input["url-input"])

        return Sentilecto.analyze(get_input_text(), output_demo_debug=debug_output)

    except Exception:
        print format_exc()

        if debug_mode:
            web.template.render().exception(format_exc(), "")

        return None


class Favicon_request:
    def GET(self):
        f = open('static/favicon.ico', 'rb')
        return f.read()


class Index_request:
    def GET(self):
        global request_id, debug_mode
        request_id += 1
        generate_captcha(request_id)
        index = web.template.frender('templates/index.html')
        return index(str(request_id), debug_mode)


class Tests_request:
    def GET(self):
        request_id = 999
        index = web.template.frender('templates/tests.html')
        return index(str(request_id))


class RunTests_request:
    def GET(self):
        # 20160211 - Daniel Cantarín
        # We execute the "run_tests" scripts, and return the output.

        path = os.path.dirname(os.path.realpath(__file__))

        subprocess.call(path + "/../run_tests", shell=True)
        # It takes its time, then writes a file. We catch that.
        f = open(path + "/../test_results.log", "r")
        a = f.read()
        f.close()
        return a.decode("unicode-escape")


class Debug_request:
    def GET(self):
        output = StringIO("")
        sys.stdout = output
        sys.stderr = output

        print web.ctx

        input_text = get_input_text()
        language = detect_language(input_text)
        if language == u'es' or language == u'it' or language == u'fr' or language == u'ca' or language == u'as' or language == u'gl':
            analysis = analyze(debug_output=True)
            return web.template.render().debug(output.getvalue())
        elif language == u'pt':
            # return web.template.render().ptresult()
            return redirect_to_pt(input_text, "debug")
        else:
            return web.template.render().unsupported()

        # analyze(debug_output=True)
        # return web.template.render().debug(output.getvalue())


class HiddenEntiNews_request:
    def GET(self):

        input_text = get_input_text()
        language = detect_language(input_text)
        if language == u'es' or language == u'it' or language == u'fr' or language == u'ca' or language == u'as' or language == u'gl':
            analysis = analyze()
            return web.template.render().entinews(analysis, WebOutputUtils(ontology))
        elif language == u'pt':
            # return web.template.render().ptresult()
            return redirect_to_pt(input_text, "hidden")
        else:
            return web.template.render().unsupported()

        # analysis = analyze()

        # return web.template.render().entinews(analysis, WebOutputUtils(ontology))


class EntiNews_request:
    def action_content_rewrite(self):

        try:
            web_input = web.input()
            return web.template.render().rewrite(ContentRewriterAndGenerator().run(web_input.text))

        except Exception:
            print format_exc()
            web.redirect("/sentilecto")

    def action_content_summarize(self):
        try:
            analysis = analyze()
            return web.template.render().summary(analysis["paragraph"].text, TextSummarizer(analysis).summarize(), QuoteFinder(analysis).get_checkable_quotes())

        except Exception:
            print format_exc()
            web.redirect("/sentilecto")

    def action_content_financial(self):
        try:
            #analysis = analyze()
            analysis = Sentilecto.analyze(get_input_text().replace('\'','').replace('"',''))
            return web.template.render().financial(analysis["paragraph"].text, financial_result(analysis))

        except Exception:
            print format_exc()
            web.redirect("/sentilecto")

    def action_fact_extraction(self):
        analysis = analyze()
        if not analysis:
            web.redirect("/sentilecto")

        return web.template.render().facts(analysis, WebOutputUtils(ontology))

    def action_svo_slots(self):
        analysis = analyze()
        if not analysis:
            web.redirect("/sentilecto")

        return web.template.render().entinews(analysis, WebOutputUtils(ontology))

    def action_english(self):
        import json
        response = ApiConnector().make_request(get_input_text())
        try:
            test_result = json.dumps(response, sort_keys=True, indent=4)
        except Exception as e:
            test_result = None

        if not test_result:
            web.redirect("/sentilecto")
        return web.template.render().english(test_result, WebOutputUtils(ontology))

    def POST(self):

        web_input = web.input()
        incoming_request_id = int(web_input.request)

        request_captcha = right_captcha = 1
        if not debug_mode:
            request_captcha = web_input.captcha

        if incoming_request_id in request_data:
            if not debug_mode:
                right_captcha = request_data[incoming_request_id]["captcha"]
            cleanup_session(incoming_request_id)

            if debug_mode or request_captcha == right_captcha:
                logger = logging.getLogger("requests")

                web_env = web.ctx["environ"]
                ip = web_env["HTTP_X_FORWARDED_FOR"] if "HTTP_X_FORWARDED_FOR" in web_env else web.ctx["ip"]
                logger.info(time.strftime("%d/%m/%Y %H:%M:%S") + "\t" + ip + "\t" + web.ctx["fullpath"])

                action_by_method = {"svo_slots" 		: self.action_svo_slots,
                                    "fact_extraction"	: self.action_fact_extraction,
                                    "content_rewrite"	: self.action_content_rewrite,
                                    "content_summarize": self.action_content_summarize,
                                    "financial_compliance": self.action_content_financial,
                                    "english"             : self.action_english}

                method = web_input["method"]

                logger.info("Detecting language:")

                input_text = get_input_text()
                language = detect_language(input_text)
                logger.info("Language is: " + language)

                if language == u'es' or language == u'it' or language == u'fr' or language == u'ca' or language == u'as' or language == u'gl':
                    return action_by_method[method]()
                elif language == u'pt':
                    # return web.template.render().ptresult()
                    return redirect_to_pt(input_text, "result", web_input)
                elif method == 'english':
                    return action_by_method[method]()
                else:
                    return web.template.render().unsupported()

        web.redirect("/sentilecto")


# 20160217 - Daniel Cantarín
# Spanish sentilecto's demo needs to redirect data to Portuguese.
# This function handles that logic.
def redirect_to_pt(text, point, web_input=None):
    numero = random.random()
    archivo = "/tmp/sentilecto-redirect-" + str(numero)
    print "Escribiendo archivo \"" + archivo + "\"..."
    f = open(archivo, "w")

    if web_input is not None:
        for key in web_input:
            f.write(key.encode("utf-8") + ":" + web_input[key].encode("utf-8") + "\n")

    f.write("--------------------\n".encode("utf-8"))
    f.write(text.encode("utf-8"))
    f.close()
    # f = codecs.open(archivo, "r", "utf-8")
    # print "Contenido del archivo: " + f.read().decode('string-escape').decode("utf-8")
    # f.close()

    url = "/sentiportugues/" + point + "?n=" + str(numero)
    print "Redireccionando hacia \"" + url + "\" ..."
    return web.seeother(url)

# # # MAIN # # #


def write_pid_file():
    pid = str(os.getpid())
    pid_file = './sentilecto.pid'
    file(pid_file, 'w').write(pid)


def setup_loggers():
    logger_names = ["requests", "exceptions", "tecnonews"]
    for name in logger_names:
        logger = logging.getLogger(name)
        logger.addHandler(logging.FileHandler(name + ".log"))
        logger.setLevel(logging.INFO)


if __name__ == '__main__':
    print 'launching...'

    urls = ('/',            'Index_request',
            '/result',      'EntiNews_request',
            '/hidden',      'HiddenEntiNews_request',
            '/debug',       'Debug_request',
            '/tests',       'Tests_request',
            '/run_tests',   'RunTests_request',
            '/favicon.ico', 'Favicon_request')

    write_pid_file()
    setup_loggers()

    cleanup_timer = Timer(30, cleanup_sessions)
    cleanup_timer.start()

    app = web.application(urls, globals())
    app.run()
