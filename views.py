from flask import Blueprint, render_template, redirect, url_for,request, flash
from models import Student, Trip, db
from flask_login import login_required
import io
import csv

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

@main.route('/move-student', methods=['POST'])
@login_required
def move_student():
    student_input = request.form.get('student_name', '').strip()
    new_trip_id = request.form.get('new_trip_id')

    # Find the student
    student = Student.query.filter(
        (Student.student_id == student_input) |
        (Student.first_name.ilike(f"%{student_input}%")) |
        (Student.last_name.ilike(f"%{student_input}%")) |
        ((Student.first_name + ' ' + Student.last_name).ilike(f"%{student_input}%"))
    ).first()

    # Find the new trip
    new_trip = Trip.query.get(new_trip_id)

    if not student or not new_trip:
        return {"success": False, "message": "⚠️ Student or trip not found."}, 400

    old_trip_name = student.trip.trip_name if student.trip else "None"

    student.trip_id = new_trip.id
    db.session.commit()
    return redirect(url_for('main.groups'))




@main.route('/swap-students', methods=['POST'])
@login_required
def swap_students():
    s1_input = (request.form.get('student1_name') or "").strip()
    s2_input = (request.form.get('student2_name') or "").strip()

    # Find both students
    student1 = Student.query.filter(
        (Student.student_id == s1_input) |
        (Student.first_name.ilike(f"%{s1_input}%")) |
        (Student.last_name.ilike(f"%{s1_input}%")) |
        ((Student.first_name + ' ' + Student.last_name).ilike(f"%{s1_input}%"))
    ).first()

    student2 = Student.query.filter(
        (Student.student_id == s2_input) |
        (Student.first_name.ilike(f"%{s2_input}%")) |
        (Student.last_name.ilike(f"%{s2_input}%")) |
        ((Student.first_name + ' ' + Student.last_name).ilike(f"%{s2_input}%"))
    ).first()

    if student1 and student2:
        # Swap their trips
        temp = student1.trip_id
        student1.trip_id = student2.trip_id
        student2.trip_id = temp
        db.session.commit()

    # quietly return to Groups
    return redirect(url_for('main.groups'))





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

@main.route('/upload_csv', methods=['POST'])
def upload_csv():
    file = request.files.get('csv_file')
    if not file:
        flash('No file selected.', 'danger')
        return redirect(url_for('main.groups'))

    try:
        # Read CSV content
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.DictReader(stream)

        for row in csv_input:
            # Expecting CSV columns like:
            # student_id,first_name,last_name,trip_name,trip_type,gender,athletic_team,hometown,dorm,water_comfort,tent_comfort
            trip_name = row.get('trip_name', '').strip()

            # Find or create the trip
            trip = Trip.query.filter_by(trip_name=trip_name).first()
            if not trip:
                trip = Trip(trip_name=trip_name, trip_type=row.get('trip_type', ''))
                db.session.add(trip)
                db.session.flush()

            # Find or create the student
            student = Student.query.filter_by(student_id=row.get('student_id')).first()
            if not student:
                student = Student(
                    student_id=row.get('student_id'),
                    first_name=row.get('first_name'),
                    last_name=row.get('last_name'),
                    gender=row.get('gender'),
                    athletic_team=row.get('athletic_team'),
                    hometown=row.get('hometown'),
                    dorm=row.get('dorm'),
                    water_comfort=row.get('water_comfort'),
                    tent_comfort=row.get('tent_comfort'),
                    trip_id=trip.id
                )
                db.session.add(student)
            else:
                # If student already exists, just update their trip
                student.trip_id = trip.id

        db.session.commit()
        flash('CSV uploaded and database updated successfully!', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error processing CSV: {str(e)}', 'danger')

    return redirect(url_for('main.groups'))

