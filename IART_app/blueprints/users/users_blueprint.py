
from flask import render_template, request, flash, redirect, url_for, Blueprint
from flask_login import login_user, current_user, login_required, logout_user
import os
from flask import current_app 
from blueprints.users.forms import RegisterForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from project.models_db import User, Connection
from build_app import db, mail
from datetime import datetime
from flask_mail import Message, Mail

users_blueprint = Blueprint(name='users', import_name=__name__, template_folder=None)

DIR= os.path.dirname(os.path.abspath(__file__))


# Only needed on first execution to create first user
#@users_blueprint.before_app_first_request
def create_admin_user():
    admin_user  =  User(current_app.config['ADMIN'], 'admin', 'admin',role='admin') # email, username, plaintext_password, role
    db.session.add(admin_user)
    db.session.commit()


@users_blueprint.route('/profile',methods=['GET', 'POST'])
@login_required
def profile():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    return render_template('profile.html', title='Profile', form=form)



@users_blueprint.route("/register", methods=['GET', 'POST'])
def register():
    # If the User is already logged in, don't allow them to try to register
    if current_user.is_authenticated:
        flash('Already registered! Redirecting to your User Profile page...')
        return redirect(url_for('users.profile'))

    form = RegisterForm()
    if request.method == 'POST' and form.validate_on_submit():
        # le password est haché dans models_db.py
        new_user  =  User(form.email.data, form.username.data, form.password.data)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        connection_on = datetime.now()
        connection = Connection(form.email.data, connected_on=connection_on)
        db.session.add(connection)
        db.session.commit()
        flash(f'Thanks for signing up! Account created for {new_user.username}.')
        return redirect(url_for('users.profile'))
    return render_template('register.html', title='Register', form=form)


@users_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    # If the User is already logged in, don't allow them to try to log in again
    if current_user.is_authenticated:
        flash('Already logged in! Redirecting to your User Profile page...')
        connection_on = datetime.now()
        
        connection = Connection(current_user.email, connected_on=connection_on)
        db.session.add(connection)
        db.session.commit()
        return redirect(url_for('users.profile'))

    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and user.is_correct_password(form.password.data):
                login_user(user, remember=form.remember.data)
                connection_on = datetime.now()
                connection = Connection(form.email.data,  connected_on=connection_on)
                db.session.add(connection)
                db.session.commit()
                flash(f'You have been logged in!')
                return redirect(url_for('users.profile'))
            else:
                flash('Login Unsuccessful. Please check email and password')

    return render_template('login.html', title='Login', form=form)


@users_blueprint.route("/logout")
@login_required
def logout():
    user = current_user
    connection_off = datetime.now()
    connection = Connection(current_user.email, connected_off=connection_off)
    db.session.add(connection)
    db.session.commit()
    logout_user()
    flash('Goodbye!')
    return redirect(url_for('home.welcome'))


@users_blueprint.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home.welcome'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@users_blueprint.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home.welwome'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password = form.password.data
        db.session.commit()
        flash('Your password has been updated! You are now able to log in')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message(subject='Flask App IART Password Reset',
                sender='noreply@IART.com',
                recipients=[user.email])

    msg.html = render_template('email_reset_password.html',user=user, token=token)
    mail.send(msg)
