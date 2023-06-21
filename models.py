from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from uuid import uuid4
from datetime import datetime


db = SQLAlchemy()

def get_uuid():
    return uuid4().hex

class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.String(32), primary_key = True, unique=True, default=get_uuid)
    email = db.Column(db.String(345), unique=True)
    password = db.Column(db.Text(72), nullable=False)
    name = db.Column(db.String(32))
    emission = db.relationship('Emission', backref='user', lazy=True)

class Emission(db.Model):
    __tablename__ = "emissions"
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    datetime = db.Column(db.DateTime, default=datetime.utcnow)
    week_number = db.Column(db.Integer, default=datetime.utcnow.iscalendar()[1])
    year = db.Column(db.Integer, default=datetime.utcnow.year)
    plastic_emission = db.Column(db.Float, default = 0.0)
    carbon_emission = db.Column(db.Float, default = 0.0)
    category = db.Column(db.String(32), nullable=False)

