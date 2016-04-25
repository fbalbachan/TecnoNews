# -*- coding: utf-8 -*-

from flask import Flask, render_template, redirect, url_for, session, escape, request


app = Flask(__name__)
app.config.from_object('config')

@app.route('/')
def hello_world():
    return render_template("index.html", app=app)

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == "hola" and request.form["password"] == "hola" :
            return "hola"
        else :
            return "usuario o contraseña incorrectos."
    return render_template('login.html', app=app)

if __name__ == '__main__':
    app.run()
