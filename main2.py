from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import check_password_hash
from flask_login import login_required, login_user, current_user
from forms import LoginForm
import main as main

app = Flask(__name__)


@app.route('/login/', methods=['post', 'get'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for(current_user))
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = main.User.find_by_username(username)
        if check_password_hash(user.password, password):
            login_user(user, remember=form.remember.data)
            return redirect(url_for(current_user))
        else:
            flash("Неправильные имя пользователя или пароль", 'error')
            return redirect(url_for('login'))
    return render_template('login.html', form=form)