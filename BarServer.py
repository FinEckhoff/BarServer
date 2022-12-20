import hashlib

import flask
import flask_login
import mysql.connector
from flask_wtf import FlaskForm
from mysql.connector import errorcode
import configparser
from flask import Flask, jsonify, request, redirect, make_response, render_template
from flask_login import LoginManager, login_required, UserMixin, login_user
import math
from wtforms import StringField, PasswordField, SubmitField


def get_user_id(uname):
    query = f"SELECT id from user where name = '{uname}'"
    cursor.execute(query)
    results = cursor.fetchall()
    if len(results) == 0:
        print(f"no such user found {uname}")
        return None
    return str(results[0])


class User(UserMixin):
    userList = []

    def __init__(self):
        self.uName = ""
        self.uid = -1

    def setup(self):
        self.uid = -1
        self.uName = ""


    def get_id(self) -> str:
        get_user_id(self.uName)


        return str(self.uid)

    def get(uid : str):
        filteredList = list(filter(lambda user: user.get_id() == uid, User.userList))
        if len(filteredList) > 1:
            pass
            # HÄÄÄ
        if len(filteredList) == 0:
            print("failed user")
            return None

        return filteredList[0]


class Order:
    def __init__(self, drinkID: int, barID: int, menge: int):
        self.drinkID = drinkID
        self.barID = barID
        self.menge = menge

    def close(self):
        orderQueue.remove(self)

    def __str__(self):
        return str((vars(self)))


app = Flask(__name__, template_folder="./templates")

app.config.update(
    DEBUG=True,
    SECRET_KEY="secret_sauce",
    SESSION_COOKIE_HTTPONLY=True,
    REMEMBER_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Strict",
)

login_manager = LoginManager()
login_manager.init_app(app)

config = configparser.ConfigParser()
config.read("config.cnf")
MySQLConfig = config["MYSQL"]

cnx = mysql.connector.connect(user=MySQLConfig["user"], password=MySQLConfig["password"], host='localhost',
                              database=MySQLConfig["database"])

cursor = cnx.cursor()
orderQueue = []


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@app.route("/settings")
@login_required
def settings():
    print(flask_login.current_user.uid)
    return "Geile sache"


@app.route('/api/getBeverages')
def get_beverages():
    query = 'SELECT id,Name,Img_URL from beverages'
    cursor.execute(query)
    results = cursor.fetchall()
    ret = []
    for result in results:
        ret.append(result)

    newret = []
    if len(ret) % 2 == 1:
        ret.append(())
    for i in range(0, math.ceil(len(ret)/2)):
        newret.append((ret[i], ret[i+1]))
    id = -1
    if not flask_login.current_user.is_anonymous:
        id = flask_login.current_user.uid

    return render_template("getBeverage.html", beverages = newret, userID = id)


@app.route('/api/orderNew')
@login_required
def set_order():
    drinkID = int(request.args.get('drinkID'))
    barID = int(request.args.get('barID'))
    menge = int(request.args.get('menge'))

    _order = Order(drinkID, barID, menge)
    orderQueue.append(_order)
    print(_order)
    flask.flash('Send')
    return render_template('confirm.html', target='/api/getBeverages')


@app.route('/api/getOrderQueue')
def get_order():
    barID = int(request.args.get('barID', "-1"))
    ret = []
    if barID == -1:
        ret = list(map(lambda order: str(order), orderQueue))
    else:
        filtered = filter(lambda order: order.barID == barID, orderQueue)
        ret = list(map(lambda order: str(order), filtered))
    return jsonify(ret)


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
        User.userList.append(user) # What is a memory leak????
        login_user(user)

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
    # logout_user()
    return redirect("index")


def validate_user(username, password):
    if username.type is None or password.type is None:
        return False
    if username.data == "" or password.data == "":
            return False
    try:
        hash =  hashlib.md5(password.data.encode())
        query = f"SELECT id from user where name = '{username.data}' and pass = '{hash.hexdigest()}'"
        cursor.execute(query)
        results = cursor.fetchall()
        print(hash.hexdigest())
        return len(results) == 1

    except Exception as e:
        print (e)
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
