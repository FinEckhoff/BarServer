import configparser
import json
import re
from mysql.connector import errorcode
import mysql.connector
from flask_login import UserMixin

config = configparser.ConfigParser()
config.read("config.cnf")
MySQLConfig = config["MYSQL"]
cnx = mysql.connector.connect(user=MySQLConfig["user"], password=MySQLConfig["password"], host=MySQLConfig["host"],
                              database=MySQLConfig["database"], port=MySQLConfig["port"])
orderQueue = []

cursor = cnx.cursor()

config = configparser.ConfigParser()
config.read("config.cnf")


class User(UserMixin):
    userList = []

    def __init__(self):
        self.gruppe = ""
        self.home = ""
        self.uName = ""
        self.uid = -1
        self.cart = {}

    def setup(self):
        self.uid = -1
        self.uName = ""
        self.cart = {}

    def get_id(self):
        return str(self.uid)


    @staticmethod
    def get(uid: str):
        """
        @param uid: the unique UserId fpr this user
        @see MySQL user.id
        @return:
        """
        filteredList = list(filter(lambda user: user.get_id() == uid, User.userList))
        if len(filteredList) > 1:
            pass
            # HÄÄÄ
        if len(filteredList) == 0:
            print("failed user")
            return None

        return filteredList[0]

    def get_cart(self):
        return json.dumps(self.cart)

    def addItemToCart(self, itemId):
        if itemId in self.cart.keys():
            self.cart[itemId] = self.cart[itemId] + 1
        else:
            self.cart[itemId] = 1

    def removeItemFromCart(self, itemId):
        if itemId not in self.cart.keys():
            return  # TODO confused
        self.cart[itemId] = self.cart[itemId] - 1
        if self.cart[itemId] == 0:
            self.cart.pop(itemId, None)

    def sync(self):
        query = f"SELECT *  from user where name = '{self.uName}'"
        cursor.execute(query)

        row_headers = [x[0] for x in cursor.description]
        results = cursor.fetchall()
        if len(results) == 0:
            print(f"no such user found {self.uName}")
            return None
        json_data = []
        for result in results:
            json_data.append(dict(zip(row_headers, result)))

        userInfo = json.loads(json.dumps(json_data))[0]
        self.gruppe = userInfo["gruppe"]
        self.uid = userInfo["id"]
        HomeConfig = config["HOME"]
        self.home = HomeConfig[str(self.gruppe)]


class Order:
    def __init__(self, drinkID: int, barID: int, menge: int):
        self.drinkID = drinkID
        self.barID = barID
        self.menge = menge

    def close(self):
        orderQueue.remove(self)

    def __str__(self):
        return str((vars(self)))

    def __eq__(self, other):  # ich habe auf meinen PC gekotzt als ich das geschreiben habe
        if not isinstance(other, Order):

            return False
        if not int(self.barID) == int(other.barID):

            return False
        if not int(self.drinkID) == int(other.drinkID):

            return False

        return True

    def __ne__(self, other):
        return not self.__eq__(other)
