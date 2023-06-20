from flask import Flask, request, jsonify, session
from flask_bcrypt import Bcrypt
from config import ApplicationConfig
from models import db, User
from flask_session import Session
from calculate import calculator
from flask_cors import CORS
from flask_login import LoginManager, login_user, current_user, login_required

app = Flask(__name__)
app.config.from_object(ApplicationConfig)

CORS(app, supports_credentials=True)

db.init_app(app)
server_session = Session(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)

@app.route('/token', methods=['GET'])
def create_token():
    if current_user.is_authenticated:
        return jsonify({
            "email": current_user.email,
            "id": current_user.id})

    else:
        return jsonify({
            "error": "User not authenticated!"
        })


with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
    return "Hello world"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/calculate', methods=['GET'])
def calculate():

    mtup = calculator('k1', 5, 'd')
    a,b = mtup

    return jsonify({
        "weight": a,
        "emission": b
    })

@app.route('/login', methods=['POST'])
def login():

    email = request.json["email"]
    password = request.json["password"]

    user = User.query.filter_by(email=email).first()

    if user is None:
        return jsonify({"error": "Unauthorized"}), 401
    
    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "Unauthorized"}), 401
    
    login_user(user)
    
    return jsonify({
        "id": user.id,
        "email": user.email
    })
#     form = LoginForm()
#     error = ''
#     if form.validate_on_submit():

#         user = User.query.filter_by(email=form.email.data).first()

#         if user is not None and user.check_password(form.password.data):

#             login_user(user)

#             next = request.args.get('next')
#             if next == None or not next[0] == '/':
#                 next = url_for('calculator')
#             return redirect(next)
#         elif user is not None and user.check_password(form.password.data) == False:
#             error = 'Wrong Password'
#         elif user is None:
#             error = 'No such login Pls create one'
    # return render_template('login.htm')


@app.route('/register', methods=['POST'])
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

    return jsonify({
        "id": new_user.id,
        "email": new_user.email
    })

    # form = RegistrationForm()
    # if form.validate_on_submit():

    #     user = User(name=form.name.data,
    #                 username=form.username.data,
    #                 email=form.email.data,
    #                 password=form.password.data)
    #     db.session.add(user)
    #     db.session.commit()

    #     if form.picture.data is not None:
    #         id = user.id
    #         pic = add_profile_pic(form.picture.data, id)
    #         user.profile_image = pic
    #         db.session.commit()
    #     return redirect(url_for('login'))
    # return render_template('register.htm', form=form)


# @app.route('/account', methods=['GET', 'POST'])
# @login_required
# def account():
#     return "hello world!"
#     pic = current_user.profile_image
#     form = UpdateUserForm()
#     if form.validate_on_submit():
#         current_user.email = form.email.data
#         current_user.username = form.username.data

#         if form.picture.data is not None:
#             id = current_user.id
#             pic = add_profile_pic(form.picture.data, id)
#             current_user.profile_image = pic

#         flash('User Account Created')
#         db.session.commit()
#         return redirect(url_for('account'))
#     elif request.method == 'GET':
#         form.username.data = current_user.username
#         form.email.data = current_user.email

#     profile_image = url_for('static', filename=current_user.profile_image)


if __name__ == '__main__':
    app.run(debug=True)
