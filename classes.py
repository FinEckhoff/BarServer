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

class User(UserMixin):

    userList = []

    def __init__(self):

        self.uName = ""
        self.uid = -1
        self.cart = {}

    def setup(self):
        self.uid = -1
        self.uName = ""
        self.cart = {}

    def get_id(self) -> str:

        self.uid = User.get_user_id(self.uName)
        return str(self.uid)

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

    def addItemToCart(self, id):
        if id in self.cart.keys():
            self.cart[id] = self.cart[id] + 1
        else:
            self.cart[id] = 1

    def removeItemFromCart(self, id):
        if id not in self.cart.keys():
            return #TODO confused
        self.cart[id] = self.cart[id] - 1
        if self.cart[id] == 0:
            self.cart.pop(id, None)


    @staticmethod
    def get_user_id(uname):
        query = f"SELECT id from user where name = '{uname}'"
        cursor.execute(query)
        results = cursor.fetchall()
        if len(results) == 0:
            print(f"no such user found {uname}")
            return None
        # print(f"return from server for uid: {results[0]}")
        id = re.findall(r'\d+', str(results[0]))[0]
        return str(id)

class Order:
    def __init__(self, drinkID: int, barID: int, menge: int):
        self.drinkID = drinkID
        self.barID = barID
        self.menge = menge

    def close(self):
        orderQueue.remove(self)

    def __str__(self):
        return str((vars(self)))

