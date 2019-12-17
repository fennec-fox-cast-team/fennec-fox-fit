from flask_login import current_user, login_user, logout_user, login_required
from flask import render_template, flash, redirect, url_for, jsonify, abort, request
from sqlalchemy import func, cast, Date, desc
import calendar
import xml.etree.ElementTree as etree
import datetime
from app.errors import *
from app.models import User, Dinner, Meal, Portion
from app.forms import RegistrationForm, LoginForm
import PIL
from app.model.main import get_prediction


@app.route('/')
def index():
    recent_activity = get_recent_activity()
    return render_template('index.html', activity=recent_activity)


def get_recent_activity():
    recent_registered_users = User.query.order_by(User.registration_date).limit(20).all()
    dinners = Dinner.query.order_by(desc(Dinner.date)).limit(20).all()

    actions_ordered_by_date = []
    for user in recent_registered_users:
        actions_ordered_by_date.append({
            'Date': str(user.registration_date),
            'Action': 'User {} has joined the community!'.format(user.username)
        })

    for dinner in dinners:
        portions_names = [(Meal.query.get(Portion.query.get(i.id).meal_id).name) for i in dinner.portions]
        actions_ordered_by_date.append({
            'Date': str(dinner.date),
            'Action': 'User {} ate {}.'.format(User.query.get(dinner.user_id).username, ', '.join(portions_names))
        })
    actions_ordered_by_date.sort(key=lambda x: x['Date'], reverse=True)
    return actions_ordered_by_date[:15]


################ Autentifiaction

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
        user = User(username=form.username.data, email=form.email.data, role=form.role.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


################

@app.route('/calendar')
def calendar_show():
    # text_calendar = calendar.HTMLCalendar(calendar.MONDAY)
    this_month = datetime.date.today().month
    this_year = datetime.date.today().year
    # required_calendar = text_calendar.formatmonth(this_year, this_month)
    username = current_user.username
    required_calendar = get_formatted_calendar(this_year, this_month, username.lower()).replace(b'\n', b'').decode("utf-8")
    return render_template('calendar.html', calendar=required_calendar)


@app.route('/<username>/<date>')
def date_by_user(username, date):
    date = datetime.date(*[int(i) for i in date.split('-')])
    # date = datetime.datetime.strptime(date, '%Y-%m-%d')
    user = User.query.filter(func.lower(User.username) == username).first()

    if user is None:
        return abort('User "{}" not found!'.format(username))

    dinners = db.session.query(Dinner).filter(Dinner.user_id == user.id).filter(cast(Dinner.date, Date) == date).all()
    dinners2meals = []

    for i, dinner in enumerate(dinners):
        sum_nutrition = 0
        dinners2meals.append({
            'time': dinner.date,
            'meals': [],
            'name': 'Dinner ' + str(i + 1)
        })
        for portion in dinner.portions:
            meal = Meal.query.filter_by(id=portion.meal_id).first()
            sum_nutrition += meal.nutrition_value / 100. * portion.weight
            dinners2meals[i].update({'meals': dinners2meals[i]['meals'] + [{
                'name': meal.name,
                'time': dinner.date,
                'weight': portion.weight,
                'nutrition_value': meal.nutrition_value / 100. * portion.weight,
                'vitamins': meal.vitamins
            }]})
        dinners2meals[i].update({'sum_nutrition': sum_nutrition})

    # print(dinners2meals)
    return render_template('dinner_by_date.html', dinners=dinners2meals)


@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST' and 'photo' in request.files:
        img = PIL.Image.open(request.files['photo'])
        return get_prediction(img)

    return ''

import json

@login_required
@app.route('/add_dinner', methods=['GET', 'POST'])
def add_dinner():
    if request.method == 'POST':
        data = request.get_json()
        dinner = Dinner(user_id=current_user.id)

        meals_names = []
        meals_weights = []
        print(data)
        # print(type(data))
        # input()
        for meal in data:
            meals_names.append(meal['name'])
            meals_weights.append(meal['weight'])

        meals = Meal.query.filter(func.lower(Meal.name).in_([meal_name.lower() for meal_name in meals_names])).all()

        for i, j in enumerate(meals):
            p = Portion(meal_id=j.id, weight=float(meals_weights[i]))
            dinner.portions.append(p)

        db.session.add(dinner)
        db.session.commit()

        return '200, Ok'
    return render_template('upload.html')


@app.route('/hey')
def hey():
    return 'Ok!'


def get_formatted_calendar(year, month, username):
    myCal = calendar.HTMLCalendar(calendar.MONDAY)
    htmlStr = myCal.formatmonth(year, month)
    htmlStr = htmlStr.replace("&nbsp;", " ")

    root = etree.fromstring(htmlStr)
    for elem in root.findall("*//td"):
        if elem.text.isdigit():
            new_elem = etree.Element('a')
            new_elem.text = elem.text
            new_elem.set('href', url_for('date_by_user', username=username,
                                         date=str(year) + '-' + str(month) + '-' + str(new_elem.text)))
            elem.append(new_elem)
            elem.text = ''

    return etree.tostring(root)
