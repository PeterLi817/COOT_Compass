from flask import Blueprint, render_template, redirect, url_for, flash
from flask import request
from models import db, User
from flask_login import login_user, login_required, logout_user

auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
      email = request.form['email']
      password = request.form['password']
      user = User.query.filter_by(email=email).first()
      print(email, password)
      if user and user.check_password(password):
          login_user(user)
          return redirect(url_for('main.groups'))
      else:
          flash('Invalid email or password. Please try again.')
          return redirect(url_for('auth.login'))
  return render_template('login.html')

@auth_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))