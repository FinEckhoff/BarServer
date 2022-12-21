import hashlib
import json
import re
import flask
import flask_login
import mysql.connector
from flask_wtf import FlaskForm
from mysql.connector import errorcode
import configparser
from flask import Flask, jsonify, request, redirect, make_response, render_template, send_from_directory
from flask_login import LoginManager, login_required, UserMixin, login_user, logout_user
import math
from wtforms import StringField, PasswordField, SubmitField
from api import app, login_manager, orderQueue, cnx, cursor
from classes import User, Order








@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login?next=' + request.path)

@app.route("/settings")
@login_required
def settings():
    print(flask_login.current_user.uid)
    return "Geile sache"


@app.route('/')
@app.route('/index')
def index():
    user_info = {}
    if flask_login.current_user.is_anonymous:
        user_info = {
            'name': 'user'
        }
    else:
        user_info = {
            'name': flask_login.current_user.uName
        }

    return render_template('index.html', user=user_info)



@app.route('/login', methods=['GET', 'POST'])
def login():
    # Here we use a class of some kind to represent and validate our
    # client-side form data. For example, WTForms is a library that will
    # handle this for us, and we use a custom LoginForm to validate.
    form = LoginForm()
    if form.validate_on_submit():
        # Login and validate the user.
        # user should be an instance of your `User` class

        user: User = User()
        user.setup()
        user.uName = form.username.data

        User.userList.append(user)  # What is a memory leak???? #TODO fix
        login_user(user)

        user.uid = user.get_id()
        print(user.uid)

        flask.flash('Logged in successfully.')

        next = flask.request.args.get('next')
        # is_safe_url should check if the url is safe for redirects.
        # See http://flask.pocoo.org/snippets/62/ for an example.

        if not str(next):  # TODO better
            print(next)
            return flask.abort(400)
        return flask.redirect(next or flask.url_for('index'))
    return flask.render_template('login.html', form=form)


@app.route("/logout")
@login_required
def logout():
    flask_login.current_user.cart = {}
    logout_user()
    return redirect("index")


def validate_user(username, password):
    if username.type is None or password.type is None:
        return False
    if username.data == "" or password.data == "":
        return False
    try:
        hash = hashlib.md5(password.data.encode())
        query = f"SELECT id from user where name = '{username.data}' and pass = '{hash.hexdigest()}'"
        cursor.execute(query)
        results = cursor.fetchall()
        print(hash.hexdigest())
        return len(results) == 1

    except Exception as e:
        print(e)
        return False


class LoginForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')
    submit = SubmitField('Submit')

    def validate_on_submit(self):
        print("here")
        if validate_user(self.username, self.password):
            return True
        return False


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=6969)
    cursor.close()
    cnx.close()
