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
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # datetime = db.Column(db.DateTime)
    week_number = db.Column(db.Integer)
    year = db.Column(db.Integer)
    kitchen_plastic_emission = db.Column(db.Float, default = 0.0)
    kitchen_carbon_emission = db.Column(db.Float, default = 0.0)
    bathroom_plastic_emission = db.Column(db.Float, default = 0.0)
    bathroom_carbon_emission = db.Column(db.Float, default = 0.0)
    others_plastic_emission = db.Column(db.Float, default = 0.0)
    others_carbon_emission = db.Column(db.Float, default = 0.0)


class TokenBlocklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False)

