from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime, timedelta
import sqlite3
from werkzeug.security import check_password_hash
from flask_login import login_required, login_user, current_user
from forms import LoginForm

app = Flask(__name__)


class User:
    def __init__(
            self, _id, username, password, email, serial, proficiency, name, is_active
    ):
        self.id = _id
        self.username = username
        self.password = password
        self.email = email
        self.serial = serial
        self.proficiency = proficiency
        self.name = name
        self.is_active = is_active

    @classmethod
    def find_by_serial(cls, serial):
        connection = sqlite3.connect('main.db')
        cursor = connection.cursor()
        query = "SELECT * FROM users where serial=?"
        result = cursor.execute(query, (serial,))
        row = result.fetchone()
        if row:
            user = cls(*row)
        else:
            user = None
        connection.close()
        return user

    @classmethod
    def find_by_username(cls, username):
        connection = sqlite3.connect('main.db')
        cursor = connection.cursor()
        query = "SELECT * FROM users where username=?"
        result = cursor.execute(query, (username,))
        row = result.fetchone()
        if row:
            user = cls(*row)
        else:
            user = None
        connection.close()
        return user


class Order:
    def __init__(
            self, _id, proficiency, _task_text, cnc, device_type, is_done, time, work_until=None
    ):
        self.id = _id
        self.proficiency = proficiency
        self.cnc = cnc
        self.device_type = device_type
        self.is_done = is_done
        self.time = time
        self.work_until = work_until

    @classmethod
    def find_order(cls, device_type, user_proficiency):
        order = None
        connection = sqlite3.connect('main.db')
        cursor = connection.cursor()
        query = "SELECT device_type FROM devices where id=?"
        result = cursor.execute(query, (device_type,))
        device_row = result.fetchone()
        if device_row:
            device_type = device_row[0]
        else:
            device_type = None
        if device_type:
            query = "SELECT * FROM orders WHERE is_done = 0 and device_type=? order by id"
            result = cursor.execute(query, (device_type,))
            order_row = result.fetchone()
            while order_row is not None:
                if user_proficiency > order_row[1] and not order_row[5]:
                    order = cls(*order_row)
                    order.convert_time(order.time)
                order_row = result.fetchone()
        connection.close()
        return order

    @classmethod
    def get_order(cls, order_no):
        connection = sqlite3.connect('main.db')
        cursor = connection.cursor()
        query = "SELECT * FROM orders where id=?"
        result = cursor.execute(query, (order_no,))
        order_row = result.fetchone()
        if order_row:
            order = cls(*order_row)
        else:
            order = None
        connection.close()
        return order

    def close_order(self):
        if self.is_done is False:
            connection = sqlite3.connect('main.db')
            cursor = connection.cursor()
            query = "UPDATE orders SET is_done = True WHERE id=?"
            cursor.execute(query, (self.id,))
            connection.commit()
            connection.close()
        self.is_done = True

    def convert_time(self, t):
        t = datetime.strptime(t, "%H:%M:%S")
        td = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
        self.work_until = (datetime.today() + td).isoformat()


@app.route("/access", methods=['POST'])
def access():
    data = request.json
    device_no = str(data['deviceNo'])
    authorization_id = str(data['authorizationID'])
    request_time = data['time']
    user = User.find_by_serial(authorization_id)
    if user:
        order = Order.find_order(device_no, user.proficiency)
        if order:
            return {
                'ok': True,
                'deviceNo': device_no,
                'id': authorization_id,
                'order': order.id,
                'time': request_time,
                'timedelta': order.work_until,
                'cnc': order.cnc
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
    request_time = data['time']
    order = Order.get_order(data['order'])
    order.close_order()
    return{
        'ok': True,
        'time': request_time,
    }


@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for(current_user))
    else:
        return redirect(url_for('login'))


@app.route('/login/', methods=['post', 'get'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for(current_user))
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.find_by_username(username)
        if check_password_hash(user.password, password):
            login_user(user, remember=form.remember.data)
            return redirect(url_for(current_user))
        else:
            flash("Неправильные имя пользователя или пароль", 'error')
            return redirect(url_for('login'))
    return render_template('login.html', form=form)


if __name__ == "__main__":
    app.run()