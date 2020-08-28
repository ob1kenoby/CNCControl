from flask import Flask, request
from datetime import datetime, timedelta
import sqlite3

app = Flask(__name__)  # тут поменять на нужный адрес страницы?

users = {
    '321670': {
        'id': 0,
        'username': 'mise',
        'password': 'some hash',
        'email': 'mikhaylow@mirea.ru',
        'title': 'admin',
        'name': 'Михайлов С.Р.',
        'isActive': True,
        'activeOrder': True,
        'orders': ['15', '20']
    }
}

orders = {
    '15': {
        'taskText': 'source to page',
        'isDone': False,
        'deviceType': '1',
        'time': timedelta(seconds=20),
        'cnc': ''
    },
    '20': {
        'taskText': 'source to page',
        'isDone': False,
        'deviceType': '2',
        'time': timedelta(hours=1, minutes=15),
        'cnc': 'filename'
    }
}

"""" left: type, right: device"""
devices = {
    '1': ['1', '2', '3'],
    '2': ['4']
}


class User:
    def __init__(self, _id, username, password, serial, email, proficiency, name, is_active):
        self.id = _id
        self.username = username
        self.password = password
        self.serial = serial
        self.email = email
        self.proficiency = proficiency
        self.name = name
        self.is_active = is_active


def find_by_serial(self, serial):
    connection = sqlite3.connect('main.db')
    cursor = connection.cursor()
    query = "SELECT * FROM users where serial=?"
    result = cursor.execute(query, (serial,))
    row = result.fetchone()
    if row:
        user = User(row[0], row[1], row[2], row[3], row[5], row[6], row[8])
    else:
        user = None
    connection.close()
    return user


@app.route("/access", methods=['POST'])
def access():
    data = request.json
    device_no = str(data['deviceNo'])
    authorization_id = str(data['authorizationID'])
    request_time = data['time']
    user = find_by_serial(authorization_id)
    if authorization_id in users:
        if (users[authorization_id]['isActive'] and
                users[authorization_id]['activeOrder']):
            for order in users[authorization_id]['orders']:
                if order in orders:
                    if not orders[order]['isDone']:
                        if orders[order]['deviceType'] in devices:
                            if (device_no in
                                    devices[orders[order]['deviceType']]):
                                work_until = (datetime.today() +
                                              orders[order]['time'])
                                cnc = orders[order]['cnc']
                                return {
                                    'ok': True,
                                    'deviceNo': device_no,
                                    'id': authorization_id,
                                    'order': order,
                                    'time': request_time,
                                    'timedelta': work_until.isoformat(),
                                    'cnc': orders[order]['cnc']
                                }
    return {
        'ok': False,
        'deviceNo': device_no,
        'authorizationID': authorization_id,
        'time': request_time
    }


@app.route("/order_done", methods=['POST'])
def order_done():
    data = request.json
    device_no = str(data['deviceNo'])
    order = str(data['order'])
    request_time = data['time']
    if device_no in devices[orders[order]['deviceType']]:
        orders[order]['isDone'] = True
        return{
            'ok': True,
            'time': request_time,
        }
    else:
        return {
            'ok': False,
            'time': request_time,
        }


@app.route("/")
def index():
    return ""


app.run() #или тут проверить?