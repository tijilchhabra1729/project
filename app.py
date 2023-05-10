from Tool import app, db
import os
import pandas as pd
from picture_handler import add_profile_pic
import numpy as np
from Tool.forms import RegistrationForm, LoginForm, CalculateForm, UpdateUserForm
from Tool.models import User
from flask import render_template, request, url_for, redirect, flash, abort
from flask_login import current_user, login_required, login_user, logout_user
from picture_handler import add_profile_pic
from sqlalchemy import desc, asc
from werkzeug.utils import secure_filename
from flask import send_from_directory
import csv


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template("index.htm")


@app.route('/calculator', methods=['GET', 'POST'])
@login_required
def calculator():
    form = CalculateForm()
    if form.validate_on_submit():
        d1 = form.d1.data
        d2 = form.d2.data
        d3 = form.d3.data
        d4 = form.d4.data
        d5 = form.d5.data
        d6 = form.d6.data
        d7 = form.d7.data

        d1d = ((d1*365*3) / 1000) * 6
        d2d = (((d2*52)*5) / 1000) * 3
        d3d = (((d3*52)*8) / 1000) * 1.95
        d4d = (((d4*12)*10) / 1000) * 3
        d5d = (((d5 * 52)*30) / 1000) * 3
        d6d = (((d6*52)*35) / 1000) * 6
        d7d = (((d7 * 12) * 20) / 1000) * 6.9

        total = d1d + d2d + d3d + d4d + d5d + d6d + d7d

        current_user.emission = str(total)

        print(d1d)
        print(d2d)
        print(d3d)
        print(d4d)
        print(d5d)
        print(d6d)
        print(d7d)

        db.session.commit()

        print("hello")
        print(total)
    return render_template('calculate.htm', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    error = ''
    if form.validate_on_submit():

        user = User.query.filter_by(email=form.email.data).first()

        if user is not None and user.check_password(form.password.data):

            login_user(user)

            next = request.args.get('next')
            if next == None or not next[0] == '/':
                next = url_for('calculator')
            return redirect(next)
        elif user is not None and user.check_password(form.password.data) == False:
            error = 'Wrong Password'
        elif user is None:
            error = 'No such login Pls create one'
    return render_template('login.htm', form=form, error=error)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():

        user = User(name=form.name.data,
                    username=form.username.data,
                    email=form.email.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()

        if form.picture.data is not None:
            id = user.id
            pic = add_profile_pic(form.picture.data, id)
            user.profile_image = pic
            db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.htm', form=form)


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    pic = current_user.profile_image
    form = UpdateUserForm()
    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.username = form.username.data

        if form.picture.data is not None:
            id = current_user.id
            pic = add_profile_pic(form.picture.data, id)
            current_user.profile_image = pic

        flash('User Account Created')
        db.session.commit()
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    profile_image = url_for('static', filename=current_user.profile_image)


if __name__ == '__main__':
    app.run(debug=True)
