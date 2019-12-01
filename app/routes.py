from flask_login import current_user, login_user, logout_user, login_required
from flask import render_template, flash, redirect, url_for, jsonify
from jinja2 import escape
from app import app, db
from app.errors import *
from app.models import User
from app.forms import RegistrationForm, LoginForm


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

import calendar
import datetime

@app.route('/calendar')
def calendar_show():
    text_calendar = calendar.HTMLCalendar(calendar.MONDAY)
    this_month = datetime.date.today().month
    this_year = datetime.date.today().year
    required_calendar = text_calendar.formatmonth(this_year, this_month)


    
    return render_template('calendar.html', calendar=required_calendar)


@app.route('/<user>/<date>')
def date_by_user(user, date):
    date = datetime.date(*[int(i) for i in date.split('-')])
    u = User.query.filter_by(username=user).first()
    return str(u) + str(date)


def get_formatted_calendar(cal):
    pass
