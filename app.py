from flask import Flask, request, jsonify, session
from flask_bcrypt import Bcrypt
from config import ApplicationConfig
from models import db, User, TokenBlocklist, Emission
from flask_session import Session
from calculate import calculator
from flask_cors import CORS
from datetime import datetime, timezone
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager, current_user, get_jwt
import json
from flask_view_counter import ViewCounter
import sqlite3

app = Flask(__name__)
app.config.from_object(ApplicationConfig)

CORS(app, supports_credentials=True)

db.init_app(app)
server_session = Session(app)
bcrypt = Bcrypt(app)

jwt = JWTManager(app)


def get_time_now():
    current_time = datetime.now()
    return current_time


def get_year():
    current_time = get_time_now()
    current_year = current_time.year
    return current_year


def get_week():
    current_time = get_time_now()
    current_week = current_time.isocalendar().week
    return current_week


with app.app_context():
    db.create_all()
    views = ViewCounter(app, db)

con = sqlite3.connect("instance/db.sqlite")
cur = con.cursor()


@app.route('/api/', methods=['GET', 'POST'])
def index():
    return "Hello world"


@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.id


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(id=identity).one_or_none()


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
    jti = jwt_payload["jti"]
    token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()

    return token is not None


@app.route('/api/calculate', methods=['POST'])
@jwt_required(optional=True)
def calculate():
    current_identity = get_jwt_identity()
    kitchen_plastic_total = 0
    kitchen_carbon_total = 0
    bathroom_plastic_total = 0
    bathroom_carbon_total = 0
    others_plastic_total = 0
    others_carbon_total = 0

    if current_identity:
        for i in range(7):
            a, b = calculator(request.json['Kitchen'][i]['ques_id'],
                              request.json['Kitchen'][i]['value'], request.json['Kitchen'][i]['freq'])
            kitchen_carbon_total += b
            kitchen_plastic_total += a
        for i in range(4):
            a, b = calculator(request.json['Bathroom'][i]['ques_id'],
                              request.json['Bathroom'][i]['value'], request.json['Bathroom'][i]['freq'])
            bathroom_carbon_total += b
            bathroom_plastic_total += a
        for i in range(3):
            a, b = calculator(request.json['Others'][i]['ques_id'],
                              request.json['Others'][i]['value'], request.json['Others'][i]['freq'])
            others_carbon_total += b
            others_plastic_total += a

        total_plastic_emission = round(
            kitchen_plastic_total + bathroom_plastic_total + others_plastic_total, 2)
        total_carbon_emission = round(
            kitchen_carbon_total + bathroom_carbon_total + others_carbon_total, 2)

        user = User.query.filter_by(id=current_identity).first()
        emission_old = Emission.query.filter_by(user_id=user.id).all()

        week = get_week()
        year = get_year()

        emission = Emission(user_id=user.id,

                            week_number=week,
                            year=year,
                            kitchen_plastic_emission=kitchen_plastic_total,
                            kitchen_carbon_emission=kitchen_carbon_total,
                            bathroom_carbon_emission=bathroom_carbon_total,
                            bathroom_plastic_emission=bathroom_plastic_total,
                            others_carbon_emission=others_carbon_total,
                            others_plastic_emission=others_carbon_total)
        if emission_old:
            latest_emission = emission_old[-1]
            if latest_emission.week_number == week:
                db.session.delete(latest_emission)
                # db.session.add(emission)

        # else:
        #     db.session.add(emission)
        db.session.add(emission)
        db.session.commit()

        return jsonify({
            "Kitchen_Plastic_Emission": round(kitchen_plastic_total, 2),
            "Kitchen_Carbon_Emission": round(kitchen_carbon_total, 2),
            "Bathroom_Plastic_Emission": round(bathroom_plastic_total, 2),
            "Bathroom_Carbon_Emission": round(bathroom_carbon_total, 2),
            "Others_Plastic_Emission": round(others_plastic_total, 2),
            "Others_Carbon_Emission": round(others_carbon_total, 2),
            "Total_Carbon_Emission": total_carbon_emission,
            "Total_Plastic_Emission": total_plastic_emission
        }), 200

    else:

        for i in range(7):
            a, b = calculator(request.json['Kitchen'][i]['ques_id'],
                              request.json['Kitchen'][i]['value'], request.json['Kitchen'][i]['freq'])
            kitchen_carbon_total += b
            kitchen_plastic_total += a
        for i in range(4):
            a, b = calculator(request.json['Bathroom'][i]['ques_id'],
                              request.json['Bathroom'][i]['value'], request.json['Bathroom'][i]['freq'])
            bathroom_carbon_total += b
            bathroom_plastic_total += a
        for i in range(3):
            a, b = calculator(request.json['Others'][i]['ques_id'],
                              request.json['Others'][i]['value'], request.json['Others'][i]['freq'])
            others_carbon_total += b
            others_plastic_total += a

        total_plastic_emission = round(
            kitchen_plastic_total + bathroom_plastic_total + others_plastic_total, 2)
        total_carbon_emission = round(
            kitchen_carbon_total + bathroom_carbon_total + others_carbon_total, 2)

        return jsonify({
            "Kitchen_Plastic_Emission": round(kitchen_plastic_total, 2),
            "Kitchen_Carbon_Emission": round(kitchen_carbon_total, 2),
            "Bathroom_Plastic_Emission": round(bathroom_plastic_total, 2),
            "Bathroom_Carbon_Emission": round(bathroom_carbon_total, 2),
            "Others_Plastic_Emission": round(others_plastic_total, 2),
            "Others_Carbon_Emission": round(others_carbon_total, 2),
            "Total_Carbon_Emission": total_carbon_emission,
            "Total_Plastic_Emission": total_plastic_emission
        }), 200


@app.route('/api/login', methods=['POST'])
def login():

    email = request.json["email"]
    password = request.json["password"]

    user = User.query.filter_by(email=email).first()

    if user is None:
        return jsonify({"error": "Unauthorized"}), 401

    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "Unauthorized"}), 401

    access_token = create_access_token(identity=user)

    return jsonify(access_token=access_token, name=user.name, email=user.email), 200


@app.route("/api/logout", methods=["DELETE"])
@jwt_required()
def modify_token():
    jti = get_jwt()["jti"]
    now = datetime.now(timezone.utc)
    db.session.add(TokenBlocklist(jti=jti, created_at=now))
    db.session.commit()
    return jsonify(msg="JWT revoked")


@app.route("/api/protected", methods=["GET"])
@jwt_required()
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


@app.route('/api/register', methods=['POST'])
def register():

    email = request.json["email"]
    password = request.json["password"]
    name = request.json["name"]

    # returns true if user with same email exists
    user_exists = User.query.filter_by(email=email).first() is not None

    # abort if user duplicates found
    if user_exists:
        return jsonify({"error": "User with the same email already exists"}), 409

    # password hashing
    hashed_password = bcrypt.generate_password_hash(password)

    # new user created
    new_user = User(name=name,
                    email=email,
                    password=hashed_password)

    db.session.add(new_user)
    db.session.commit()

    access_token = create_access_token(identity=new_user)

    return jsonify({
        "name": new_user.name,
        "email": new_user.email,
        "access_token": access_token
    }), 200


@app.route('/api/dashboard', methods=['GET', 'POST'])
@jwt_required()
def dashboard():
    current_identity = get_jwt_identity()
    user = User.query.filter_by(id=current_identity).first()
    emission = Emission.query.filter_by(user_id=user.id).all()

    my_list = []
    my_list2 = []

    for i in range(len(emission)):
        temp_dict = {'week': 0, 'kitchen': 0, 'bathroom': 0, 'others': 0}
        week = emission[i].week_number
        kitchen_plastic = emission[i].kitchen_plastic_emission
        bathroom_plastic = emission[i].bathroom_plastic_emission
        others_plastic = emission[i].others_plastic_emission

        temp_dict['week'] = week
        temp_dict['kitchen'] = round(kitchen_plastic, 2)
        temp_dict['bathroom'] = round(bathroom_plastic, 2)
        temp_dict['others'] = round(others_plastic, 2)

        my_list.append(temp_dict)

    for i in range(len(emission)):
        temp_dict = {'week': 0, 'kitchen': 0, 'bathroom': 0, 'others': 0}
        week = emission[i].week_number
        kitchen_carbon = emission[i].kitchen_carbon_emission
        bathroom_carbon = emission[i].bathroom_carbon_emission
        others_carbon = emission[i].others_carbon_emission

        temp_dict['week'] = week
        temp_dict['kitchen'] = round(kitchen_carbon, 2)
        temp_dict['bathroom'] = round(bathroom_carbon, 2)
        temp_dict['others'] = round(others_carbon, 2)

        my_list2.append(temp_dict)

    return jsonify({
        "plastic": my_list,
        "carbon": my_list2
    })


@app.route('/api/visitor', methods=['GET'])
@views.count
def visitor():
    count = cur.execute("select count(id) from vc_requests").fetchall()[0][0]
    return {"visitor": count}, 200

# @app.route('/api/test')
# @jwt_required
# def addrecords():
#     for i in range(2):
#         year = get_year()
#         emission = Emission(week_number=i,
#                             year=year,
#                             kitchen_plastic_emission=10)
#         db.session.add(emission)
#         db.session.commit()
#     return "Hello world, added entries"


if __name__ == '__main__':
    app.run()
