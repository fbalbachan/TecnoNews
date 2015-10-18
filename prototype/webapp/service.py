#!/usr/bin/python
# -*- coding: utf-8 -*-

from StringIO import StringIO
import logging
import os
import sys
from threading import Timer
import time
from traceback import format_exc

import web
from skimpyGimpy import skimpyAPI

from src.model.contentRewriterAndGenerator import ContentRewriterAndGenerator
from src.model.sentilecto import Sentilecto
from src.utils.webOutputUtils import WebOutputUtils
from src.utils.configProvider import ConfigProvider
from src.ling.freelingDictionaryParser import FreelingDictionaryParser

from BeautifulSoup import BeautifulSoup
import urllib2
import re


request_id = 0
request_data = {}
captchas_by_request = {}
cleanup_timer = None

config = ConfigProvider()
debug_mode = (config.get("debug", "debug") == "True")
ontology = FreelingDictionaryParser.get_ontology()


def parse_url(url):
    try:
        page=urllib2.urlopen(url)

        soup = BeautifulSoup(page.read())
        texts = soup.findAll("p")
    except Exception:
        texts = []

    textParagraphs = []
    for node in texts:
        temp = ''.join(node.findAll(text=True))
        if re.match(".*[.]$",temp):
            textParagraphs.append(temp)

    return "\n".join(textParagraphs)


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


def analyze(debug_output=False):

    try:
        web_input = web.input()
        # x = web.input(datafile={})

        text = web_input.text if ("url-input" not in web_input or web_input["url-input"] == "") \
               else parse_url(web_input["url-input"])

        return Sentilecto.analyze(text, output_demo_debug=debug_output)

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


class Debug_request:
    def GET(self):
        output = StringIO("")
        sys.stdout = output
        sys.stderr = output

        print web.ctx
        analyze(debug_output=True)
        return web.template.render().debug(output.getvalue())


class HiddenEntiNews_request:
    def GET(self):
        analysis = analyze()

        return web.template.render().entinews(analysis, WebOutputUtils(ontology))


class EntiNews_request:
    def action_content_rewrite(self):

        try:
            web_input = web.input()
            return web.template.render().rewrite(ContentRewriterAndGenerator().run(web_input.text))

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

    def GET(self):

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
                                    "content_rewrite"	: self.action_content_rewrite }

                method = web_input["method"]
                return action_by_method[method]()

        web.redirect("/sentilecto")

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
            '/favicon.ico', 'Favicon_request')

    write_pid_file()
    setup_loggers()

    cleanup_timer = Timer(30, cleanup_sessions)
    cleanup_timer.start()

    app = web.application(urls, globals())
    app.run()
