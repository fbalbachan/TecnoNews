# -*- coding: utf-8 -*-
from flask import Flask, render_template, redirect, url_for, session, escape, request
from flask.views import MethodView

class UserView(MethodView):
    def get(self):
        name = request.args.get('username', 'Damyan')
        return 'Hello GET from %s!' % name

    def post(self):
        name = request.form.get('username', 'Damyan')
        return 'Hello POST from %s' % name

