from flask import Blueprint, render_template, redirect, url_for, request, flash
from models import Student, Trip, db
from flask_login import login_required
import io
import csv

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index():
    # trips = Trip.query.all()
    return redirect(url_for('main.groups'))

@main.route('/trips')
@login_required
def trips():
    trips = Trip.query.all()
    return render_template('trips.html', trips=trips)

@main.route('/first-years')
@login_required
def first_years():
    students = Student.query.all()
    trips = Trip.query.all()
    unique_trip_types_query = db.session.query(Trip.trip_type).distinct().order_by(Trip.trip_type)
    unique_trip_types = [t[0] for t in unique_trip_types_query]
    return render_template('first-years.html', students=students, trips=trips, unique_trip_types=unique_trip_types)

@main.route('/groups')
@login_required
def groups():
    trips = Trip.query.all()
    return render_template('groups.html', trips=trips)

# @main.route('/settings')
# @login_required
# def settings():
#     return render_template('settings.html')

@main.route('/add-student', methods=['GET', 'POST'])
@login_required
def add_student():
    if request.method == 'POST':
        # Get required data from the form
        student_id = request.form.get('student_id')
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')

        # Make sure all required fields are there
        if not student_id or not email or not first_name or not last_name:
            flash('Error: One or more required fields (ID, Email, First/Last Name) are missing.', 'danger')
            return redirect(url_for('main.first_years'))
        
        # See if student id or email already exist
        if Student.query.filter((Student.student_id == student_id) | (Student.email == email)).first():
            flash(f'Error: A student with that ID or Email already exists.', 'danger')
            return redirect(url_for('main.first_years'))
        
        # Get the data from the checkboxes on the form
        # Returns true if check, None if unchecked
        poc = request.form.get('poc') == 'true'
        fli_international = request.form.get('fli_international') == 'true'
        
        # Create a new student
        new_student = Student(
            student_id=student_id,
            email=email,
            first_name=first_name,
            last_name=last_name,
            trip_pref_1=request.form.get('trip_pref_1'),
            trip_pref_2=request.form.get('trip_pref_2'),
            trip_pref_3=request.form.get('trip_pref_3'),
            dorm=request.form.get('dorm'),
            athletic_team=request.form.get('athletic_team'), 
            notes=request.form.get('notes'),
            gender=request.form.get('gender'),
            water_comfort=request.form.get('water-comfort'),
            tent_comfort=request.form.get('tent-comfort'),
            hometown=request.form.get('hometown'),
            poc=poc,
            fli_international=fli_international,
            trip_id=request.form.get('assigned-trip') or None
        )

        try:
            # Add to database and save
            db.session.add(new_student)
            db.session.commit()
            flash('Student added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error: Could not add student. {str(e)}', 'danger')

        return redirect(url_for('main.first_years'))

    return redirect(url_for('main.first_years'))
