from flask import Flask, request, jsonify, session
from flask_bcrypt import Bcrypt
from config import ApplicationConfig
from models import db, User, TokenBlocklist
from flask_session import Session
from calculate import calculator
from flask_cors import CORS
from datetime import datetime, timezone
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager, current_user, get_jwt

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

# @app.route('/api/calculate', methods=['GET'])
# @jwt_required(optional=True)
# def calculate():
#     current_identity = get_jwt_identity()
    
#     if current_identity:


#         return jsonify({
#             "weight": 1,
#             "emission": 2 
#         }), 200

@app.route('/api/login', methods=['POST'])
def login():

    email = request.json["email"]
    password = request.json["password"]

    user = User.query.filter_by(email=email).first()
    print(user)

    if user is None:
        return jsonify({"error": "Unauthorized"}), 401
    
    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "Unauthorized"}), 401
    
    access_token = create_access_token(identity=user)
    print(user)
    
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


if __name__ == '__main__':
    app.run(debug=True)

 