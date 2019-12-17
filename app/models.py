from app import db, login
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

dinners_portions = db.Table(
    'dinners_portions',
    db.Column('dinner_id', db.Integer, db.ForeignKey('dinners.id')),
    db.Column('portion_id', db.Integer, db.ForeignKey('portions.id'))
)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    registration_date = db.Column(db.DateTime, default=datetime.now)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20))

    dinners = db.relationship('Dinner', backref='user', lazy=True)

    def __repr__(self):
        return 'User {}'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Meal(db.Model):
    __tablename__ = 'meals'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True, unique=True)
    ingredients = db.Column(db.ARRAY(db.String(45)))
    recipe = db.Column(db.String(400))

    # For 100 gram
    nutrition_value = db.Column(db.Float)
    vitamins = db.Column(db.String(100))


class Portion(db.Model):
    __tablename__ = 'portions'
    id = db.Column(db.Integer, primary_key=True)
    meal_id = db.Column(db.Integer, db.ForeignKey('meals.id'), nullable=False)
    weight = db.Column(db.Float)

    dinners = db.relationship('Dinner', secondary=dinners_portions, backref=db.backref('portions', lazy='dynamic'))


class Dinner(db.Model):
    __tablename__ = 'dinners'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)