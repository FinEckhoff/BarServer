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
from api import app, login_manager, orderQueue, cnx, cursor, LoginForm, beverages, replaceTheFuckingQuotes
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
    id = -1

    if not flask_login.current_user.is_anonymous:
        id = flask_login.current_user.uid
    print(f"home is{flask_login.current_user.home}")
    return render_template("getBeverage.html", beverages=beverages, userID=id, cart=flask_login.current_user.cart,
                           home=flask_login.current_user.home)


def condenseOrders(sortedOrders: list):  # HOLY SHIT das MUSS doch besser gehen!!
    condensed = []
    objectsAlreadyProcessed = []
    for index, order in enumerate(sortedOrders):
        if order in objectsAlreadyProcessed:
            continue
        fixeddrinkID = order.drinkID
        fixedbarID = order.barID
        currentMenge = order.menge

        for otherIndex, other in enumerate(sortedOrders):
            if order is other:
                continue
            if order == other:
                currentMenge += other.menge
        order.menge = currentMenge
        condensed.append(order)
        objectsAlreadyProcessed.append(order)
    return condensed

    return None


"""
    def findIndexOforder(order):
        index = next((i for i, item in enumerate(bestellungenProBar) if item.barID == order.barID), -1)
        return index

    for order in sortedOrders:
        index = findIndexOforder(order)
        if (index >= 0) :
            if bestellungenProBar[index].drinkID == order.drinkID:
                bestellungenProBar[index].menge += order.menge
            else:
                bestellungenProBar.append(order)
        else:
            bestellungenProBar.append(order)
"""


@app.route('/getOrders')
def get_orders():
    barID = int(request.args.get('barID', "-1"))
    ret = []
    if barID == -1:
        ret = orderQueue
        # ret = list(map(lambda order: (order, orderQueue))
    else:
        filtered = []
        filtered = filter(lambda order: int(order.barID) == int(barID), orderQueue)
        # ret = list(map(lambda order: order, filtered))
        ret = list(filtered)
    userID = -1
    if not flask_login.current_user.is_anonymous:
        userID = flask_login.current_user.uid
    sortedOrders = sorted(ret, key=lambda x: x.barID, reverse=True)
    sortedOrders = condenseOrders(sortedOrders)
    # jsonString = str(list((map(lambda x: json.loads(str(x)), sortedOrders))))
    json_data = []
    for result in sortedOrders:
        stringResult = replaceTheFuckingQuotes(str(result))

        json_data.append(json.loads(str(stringResult)))

    json_Orders = json.loads(json.dumps(json_data))

    return render_template("getOrders.html", orders=json_Orders, userID=userID, beverages=beverages,
                           home=flask_login.current_user.home)


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

        user.sync()

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
