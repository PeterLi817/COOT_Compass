from flask import Blueprint, render_template
from models import Student, Trip

main = Blueprint('main', __name__)

@main.route('/')
def index():
    trips = Trip.query.all()
    return render_template('groups.html', trips=trips)

@main.route('/trips')
def trips():
    trips = Trip.query.all()
    return render_template('trips.html', trips=trips)

@main.route('/first-years')
def first_years():
    students = Student.query.all()
    return render_template('first-years.html', students=students)

@main.route('/groups')
def groups():
    trips = Trip.query.all()
    return render_template('groups.html', trips=trips)

@main.route('/settings')
def settings():
    return render_template('settings.html')

@main.route('/login')
def login():
    return render_template('login.html')
