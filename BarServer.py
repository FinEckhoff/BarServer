import mysql.connector
from mysql.connector import errorcode
import configparser
from flask import Flask, jsonify, request, redirect, make_response, render_template

app = Flask(__name__, template_folder=".")

config = configparser.ConfigParser()
config.read("config.cnf")
MySQLConfig = config["MYSQL"]

cnx = mysql.connector.connect(user=MySQLConfig["user"], password=MySQLConfig["password"], host='localhost',
                              database=MySQLConfig["database"])

cursor = cnx.cursor()
orderQueue = []


@app.route('/api/getBeverages')
def get_beverages():
    query = 'SELECT id,Name,Whatever  from beverages'
    cursor.execute(query)
    results = cursor.fetchall()
    ret = []
    for result in results:
        ret.append(result)
    return jsonify(ret)


@app.route('/api/orderNew')
def set_order():
    drinkID = int(request.args.get('drinkID'))
    barID = int(request.args.get('barID'))
    menge = int(request.args.get('menge'))

    _order = Order(drinkID, barID, menge)
    orderQueue.append(_order)
    print(_order)

    return render_template('confirm.html', target='/api/getBeverages')

@app.route('/api/getOrderQueue')
def get_order():

    barID = int(request.args.get('barID', "-1"))
    ret = []
    if barID == -1:
        ret = map(lambda order: str(order), orderQueue)
    else:
        filtered = filter(lambda order: order.barID == barID, orderQueue)
        ret = map(lambda order: str(order), filtered)
    return ret





class Order:
    def __init__(self, drinkID: int, barID: int, menge: int):
        self.drinkID = drinkID
        self.barID = barID
        self.menge = menge

    def close(self):
        orderQueue.remove(self)

    def __str__(self):
        return str((vars(self)))




if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=6969)
    cursor.close()
    cnx.close()
