
import flask_login

from flask import Flask, jsonify, request, redirect, make_response, render_template, send_from_directory
from flask_login import LoginManager, login_required, UserMixin, login_user, logout_user

from classes import *

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

cnx = mysql.connector.connect(user=MySQLConfig["user"], password=MySQLConfig["password"], host='activecell.de',
                              database=MySQLConfig["database"], port=41069)

cursor = cnx.cursor()
orderQueue = []


@app.route('/api/test.css')
def standart_stylesheet():
    return send_from_directory("templates", "test.css")

@app.route('/api/cart.js')
def cart_script():
    return send_from_directory("templates", "cart.js")

@app.route('/api/addToCart/<id>')
@login_required
def addToCart(id):
    flask_login.current_user.addItemToCart(id)
    return redirect("/api/getBeverages")

@app.route('/api/submitOrder')
@login_required
def submitOrder():

    barID = flask_login.current_user.uid

    entry = json.loads(flask_login.current_user.get_cart())
    for key in entry.keys():
        print(key)

        drinkID = key
        menge = entry[key]
        _order = Order(drinkID, barID, menge)
        orderQueue.append(_order)
        print(_order)
    #flask.flash('Send')
    flask_login.current_user.cart = {}
    return render_template('confirm.html', target='/api/getBeverages')



@app.route('/api/removeFromCart/<id>')
@login_required
def removeFromToCart(id):
    flask_login.current_user.removeItemFromCart(id)

    return redirect("/api/getBeverages")


@app.route('/api/getBeverages')
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
#cartKeys = flask_login.current_user.cart.keys(), cartValues= flask_login.current_user.cart.values()

@app.route('/api/orderNew') #deprecated
@login_required
def set_order():
    pass


@app.route('/api/getOrderQueue')
def get_order():
    global orderQueue
    barID = int(request.args.get('barID', "-1"))
    ret = []
    if barID == -1:
        ret = list(map(lambda order: str(order), orderQueue))
    else:
        filtered = []
        filtered = filter(lambda order: int(order.barID) == int(barID), orderQueue)
        """
        for order in orderQueue:
            if order.barID == int(barID):
                print("wtf")
                filtered.append(order)
            else:FRUST
                print(f" order : {order.barID} - bar : {barID}" )
                print(f" order : {type(order.barID)} - bar : {type(barID)}" )
                """

        ret = list(map(lambda order: str(order), filtered))
        print(ret)

        print(list(filtered))
        print(json.dumps(ret))
    return jsonify(ret)
