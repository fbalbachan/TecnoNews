#!/usr/bin/python
# -*- coding: utf-8 -*-

from StringIO import StringIO
import logging
import os, web
from skimpyGimpy import skimpyAPI
import sys
from threading import Timer
import time

from src.model.sentilecto import Sentilecto
from src.utils.webOutputUtils import WebOutputUtils


request_id = 0
request_data = {}
captchas_by_request = {}

cleanup_timer = None

def cleanup_sessions():
	expired = []
	for id in request_data:  # @ReservedAssignment
		start = request_data[id]["start"]
		elapsed_minutes = (time.time() - start) / 60
		if elapsed_minutes > 5: expired.append(id)
	for id in expired: cleanup_session(id)  # @ReservedAssignment
	cleanup_timer.run()

def cleanup_session(request_id):
	del request_data[request_id]
	os.remove(captcha_filename_for(request_id))

def write_pidfile():
	pid = str(os.getpid())
	pidfile = '/tmp/entinews.pid'
	file(pidfile, 'w').write(pid)

def analyze():
	try:
		web_input = web.input()
		return Sentilecto().analyze(web_input.text)
	except Exception:
		return []
		#web.template.render().exception(format_exc(), "")

def captcha_filename_for(request_id):
	return "static/captcha/captcha_" + str(request_id) + ".png"

class Favicon_request:
	def GET(self):
		f = open('static/favicon.ico', 'rb')
		return f.read()

class Index_request:
	def GET(self):
		global request_id
		request_id = request_id + 1

		captcha_key = os.urandom(2).encode("hex")
		request_data[request_id] = { "captcha": captcha_key, "start": time.time() }

		generator = skimpyAPI.Png(captcha_key)
		generator.data(captcha_filename_for(request_id))

		index = web.template.frender('templates/index.html')
		return index(str(request_id))

class Debug_request:
	def GET(self):
		output = StringIO("")
		sys.stdout = output
		sys.stderr = output

		analyze()
		return web.template.render().debug(output.getvalue())

class HiddenEntiNews_request:
	def GET(self):
		analysis = analyze()
		return web.template.render().test(analysis, WebOutputUtils())

class EntiNews_request:
	def GET(self):
		web_input = web.input()
		request_id = int(web_input.request)
		request_captcha = web_input.captcha
		right_captcha = None

		if request_id in request_data:
			right_captcha = request_data[request_id]["captcha"]
			cleanup_session(request_id)

			if request_captcha == right_captcha:
				logger = logging.getLogger("requests")

				web_env = web.ctx["environ"]
				ip = web_env["HTTP_X_FORWARDED_FOR"] if "HTTP_X_FORWARDED_FOR" in web_env else web.ctx["ip"]
				logger.info(time.strftime("%d/%m/%Y %H:%M:%S") + "\t" + ip + "\t" + web.ctx["fullpath"])

				analysis = analyze()
				return web.template.render().test(analysis, WebOutputUtils())
		web.redirect("/")

### MAIN ###

def setup_loggers():
	logger_names = ["requests", "exceptions"]
	for name in logger_names:
		logger = logging.getLogger(name)
		logger.addHandler(logging.FileHandler(name + ".log"))
		logger.setLevel(logging.INFO)

if __name__ == '__main__':
	print 'launching...'

	urls = (
 	  '/favicon.ico', 'Favicon_request',
 	  '/result', 'EntiNews_request',
 	  '/hidden', 'HiddenEntiNews_request',
 	  '/', 'Index_request',
 	  '/debug', "Debug_request"
	)

	write_pidfile()
	setup_loggers()

	cleanup_timer = Timer(30, cleanup_sessions)
	cleanup_timer.start()

	app = web.application(urls, globals())
	app.run()
