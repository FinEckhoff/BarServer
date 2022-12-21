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
from api import app, login_manager, orderQueue, cnx, cursor, LoginForm
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




@app.route('/getBeverages')
@login_required
def get_beverages():
    query = 'SELECT id,Name,Img_URL from beverages'
    cursor.execute(query)
    results = cursor.fetchall()
    ret = []
    for result in results:
        ret.append(result)

    id = -1

    if not flask_login.current_user.is_anonymous:
        id = flask_login.current_user.uid

    return render_template("getBeverage.html", beverages=ret, userID=id, cart = flask_login.current_user.cart)

@app.route('/getOrders')
def get_orders():
    barID = int(request.args.get('barID', "-1"))
    ret = []
    if barID == -1:
        ret = orderQueue
        #ret = list(map(lambda order: (order, orderQueue))
    else:
        filtered = []
        filtered = filter(lambda order: int(order.barID) == int(barID), orderQueue)
        #ret = list(map(lambda order: order, filtered))
        ret = list(filtered)
    userID = -1
    if not flask_login.current_user.is_anonymous:
        userID = flask_login.current_user.uid
    sortedOrders = sorted(ret, key=lambda x: x.barID, reverse=True)
    return render_template("getOrders.html", orders = sortedOrders, userID = userID)


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



if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=6969)
    cursor.close()
    cnx.close()
