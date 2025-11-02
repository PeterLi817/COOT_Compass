from flask import Blueprint, render_template

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/trips')
def trips():
    return render_template('trips.html')

@main.route('/first-years')
def first_years():
    return render_template('first-years.html')

@main.route('/groups')
def groups():
    return render_template('groups.html')

@main.route('/settings')
def settings():
    return render_template('settings.html')

@main.route('/login')
def login():
    return render_template('login.html')
