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
def move_student():
    trips = Trip.query.all()  # Get all trips for dropdown

    if request.method == 'POST':
        student_input = request.form.get('student').strip()
        new_trip_id = request.form.get('new_trip')

        student = Student.query.filter(
            (Student.student_id == student_input) |
            (Student.first_name.ilike(f"%{student_input}%")) |
            (Student.last_name.ilike(f"%{student_input}%"))
        ).first()

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

        temp_trip = student1.trip_id
        student1.trip_id = student2.trip_id
        student2.trip_id = temp_trip

        db.session.commit()

        return redirect(url_for('main.groups'))

    return render_template('swap_students.html')


@main.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files.get('file')

        if not file:
            return render_template('upload.html', message="No file selected.")

        import csv
        from io import TextIOWrapper

        # Read CSV file
        csv_file = TextIOWrapper(file, encoding='utf-8')
        reader = csv.DictReader(csv_file)

        added_students = 0
        added_trips = 0

        for row in reader:
            # Example CSV columns: student_id, first_name, last_name, trip_name, trip_type, email
            trip_name = row.get('trip_name')
            trip_type = row.get('trip_type')

            # Find or create trip
            trip = Trip.query.filter_by(trip_name=trip_name).first()
            if not trip:
                trip = Trip(trip_name=trip_name, trip_type=trip_type)
                db.session.add(trip)
                added_trips += 1

            # Add student
            student = Student.query.filter_by(student_id=row.get('student_id')).first()
            if not student:
                student = Student(
                    student_id=row.get('student_id'),
                    first_name=row.get('first_name'),
                    last_name=row.get('last_name'),
                    email=row.get('email'),
                    trip=trip
                )
                db.session.add(student)
                added_students += 1

        db.session.commit()

        return render_template(
            'upload.html',
            message=f"✅ Uploaded successfully! Added {added_students} students and {added_trips} new trips."
        )

    return render_template('upload.html')
