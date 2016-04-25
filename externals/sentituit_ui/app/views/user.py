# -*- coding: utf-8 -*-
from flask import Flask, render_template, redirect, url_for, session, escape, request
from flask.views import MethodView

class UserView(MethodView):
    def get(self):
        return render_template("user.html")

    def post(self, app):
        return render_template("user.html", app=app)

