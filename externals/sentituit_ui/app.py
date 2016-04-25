# -*- coding: utf-8 -*-

from flask import Flask, render_template, redirect, url_for, session, escape, request
from app.views.user import UserView

app = Flask(__name__)
app.config.from_object('config')

app.add_url_rule(
    '/user',
    view_func=UserView.as_view('user')
)

@app.route('/')
def hello_world():
    return render_template("index.html", app=app)

@app.route('/login', methods=["GET", "POST"])
def login():
    print session
    
    if "username" in session:
        return logout()
        
    if request.method == "POST":
        if request.form["username"] == "hola" and request.form["password"] == "hola" :
            session["username"] = "hola"
            return UserView().post(app)
        else :
            return "usuario o contraseña incorrectos."
    return render_template('login.html', app=app)

@app.route('/logout')
def logout():
    del session["username"]
    return render_template("index.html", app=app)

if __name__ == '__main__':
    app.run()
