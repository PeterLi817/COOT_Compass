from flask import Blueprint, render_template, redirect, url_for,request
from models import Student, Trip, db
from flask_login import login_required

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index():
    # trips = Trip.query.all()
    # return render_template('login.html', trips=trips)
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
    return render_template('first-years.html', students=students)

@main.route('/groups')
@login_required
def groups():
    trips = Trip.query.all()
    return render_template('groups.html', trips=trips)

@main.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

@main.route('/move-student', methods=['GET', 'POST'])
@login_required
def move_student():
    trips = Trip.query.all()  # Get all trips for dropdown

    if request.method == 'POST':
        student_input = request.form.get('student').strip()
        new_trip_id = request.form.get('new_trip')

        # Find student
        student = Student.query.filter(
            (Student.student_id == student_input) |
            (Student.first_name.ilike(f"%{student_input}%")) |
            (Student.last_name.ilike(f"%{student_input}%"))
        ).first()

        # Find the new trip
        trip = Trip.query.get(new_trip_id)

        if not student and not trip:
            return render_template('move_result.html', trips=trips, message="Student and Trip not found.")
        elif not student:
            return render_template('move_result.html', trips=trips, message="Student not found.")
        elif not trip:
            return render_template('move_result.html', trips=trips, message="Trip not found.")

        old_trip = student.trip.trip_name if student.trip else "None"
        student.trip_id = trip.id
        db.session.commit()
        return redirect(url_for('main.groups'))

        success_message = f"{student.first_name} {student.last_name} was moved from '{old_trip}' to '{trip.trip_name}'."
        return render_template('move_result.html', trips=trips, message=success_message, success=True, student=student)

    return render_template('move_result.html', trips=trips)


@main.route('/swap-students', methods=['GET', 'POST'])
def swap_students():
    if request.method == 'POST':
        s1_input = request.form.get('student1').strip()
        s2_input = request.form.get('student2').strip()

        student1 = Student.query.filter(
            (Student.student_id == s1_input) | 
            (Student.first_name.ilike(f"%{s1_input}%")) | 
            (Student.last_name.ilike(f"%{s1_input}%"))
        ).first()

        student2 = Student.query.filter(
            (Student.student_id == s2_input) | 
            (Student.first_name.ilike(f"%{s2_input}%")) | 
            (Student.last_name.ilike(f"%{s2_input}%"))
        ).first()

        if not student1 or not student2:
            return render_template('swap_students.html', message="One or both students not found.")

        # Swap trips
        temp_trip = student1.trip_id
        student1.trip_id = student2.trip_id
        student2.trip_id = temp_trip

        db.session.commit()

        # Redirect to Groups page to confirm
        return redirect(url_for('main.groups'))

    return render_template('swap_students.html')

