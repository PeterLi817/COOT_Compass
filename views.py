from flask import Blueprint, render_template, redirect, url_for, request, flash
from models import Student, Trip, db
from flask_login import login_required
import csv
from io import StringIO
from sort import sort_students
import json

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index():
    return redirect(url_for('main.groups'))

@main.route('/trips')
@login_required
def trips():
    trips = Trip.query.all()

    # Create a dictionary mapping trip IDs to their data for JSON
    trips_data = {}
    for trip in trips:
        trips_data[str(trip.id)] = {
            'id': trip.id,
            'trip_name': trip.trip_name,
            'trip_type': trip.trip_type,
            'capacity': trip.capacity,
            'address': trip.address or '',
            'water': trip.water if trip.water is not None else False,
            'tent': trip.tent if trip.tent is not None else False
        }

    return render_template('trips.html', trips=trips, trips_data_json=json.dumps(trips_data))

@main.route('/first-years')
@login_required
def first_years():
    students = Student.query.all()
    trips = Trip.query.all()
    unique_trip_types_query = db.session.query(Trip.trip_type).distinct().order_by(Trip.trip_type)
    unique_trip_types = [t[0] for t in unique_trip_types_query]

    # Create a dictionary mapping student IDs to their data for JSON
    students_data = {}
    for student in students:
        students_data[str(student.id)] = {
            'id': student.id,
            'student_id': student.student_id,
            'email': student.email,
            'first_name': student.first_name,
            'last_name': student.last_name,
            'dorm': student.dorm or '',
            'athletic_team': student.athletic_team or '',
            'hometown': student.hometown or '',
            'notes': student.notes or '',
            'poc': student.poc if student.poc is not None else False,
            'fli_international': student.fli_international if student.fli_international is not None else False,
            'trip_pref_1': student.trip_pref_1 or '',
            'trip_pref_2': student.trip_pref_2 or '',
            'trip_pref_3': student.trip_pref_3 or '',
            'gender': student.gender or '',
            'water_comfort': str(student.water_comfort) if student.water_comfort is not None else '',
            'tent_comfort': str(student.tent_comfort) if student.tent_comfort is not None else '',
            'trip_id': student.trip_id
        }

    return render_template('first-years.html', students=students, trips=trips, unique_trip_types=unique_trip_types, students_data_json=json.dumps(students_data))

@main.route('/groups')
@login_required
def groups():
    trips = Trip.query.all()
    students = Student.query.all()
    for trip in trips:
        trip.validations = validate_trip(trip)
        trip.current_students = len(trip.students)
        trip.has_open_slots = trip.current_students < trip.capacity
        trip.open_slots_count = trip.capacity - trip.current_students
    return render_template('groups.html', trips=trips, students=students)

@main.route('/add-student', methods=['GET', 'POST'])
@login_required
def add_student():
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')

        if not student_id or not email or not first_name or not last_name:
            flash('Error: Missing required fields.', 'danger')
            return redirect(url_for('main.first_years'))

        if Student.query.filter((Student.student_id == student_id) | (Student.email == email)).first():
            flash('Error: Student with that ID or Email already exists.', 'danger')
            return redirect(url_for('main.first_years'))

        # Get the data from the checkboxes on the form
        # Returns true if check, None if unchecked
        poc = request.form.get('poc') == 'true'
        fli_international = request.form.get('fli_international') == 'true'

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
            water_comfort=int(request.form.get('water_comfort')) if request.form.get('water_comfort') else None,
            tent_comfort=int(request.form.get('tent_comfort')) if request.form.get('tent_comfort') else None,
            hometown=request.form.get('hometown'),
            poc=poc,
            fli_international=fli_international,
            trip_id=request.form.get('assigned-trip') or None
        )

        try:
            db.session.add(new_student)
            db.session.commit()
            flash('Student added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding student: {str(e)}', 'danger')

        return redirect(url_for('main.first_years'))

    return redirect(url_for('main.first_years'))

@main.route('/edit-student', methods=['POST'])
@login_required
def edit_student():
    # Get the database primary key (id) from the hidden form field
    student_db_id = request.form.get('student_id')

    if not student_db_id:
        flash('Error: Student ID is required.', 'danger')
        return redirect(url_for('main.first_years'))

    # Query by database primary key (id), not by student_id field
    try:
        student = Student.query.get(int(student_db_id))
    except (ValueError, TypeError):
        student = None

    if not student:
        flash('Error: Student not found.', 'danger')
        return redirect(url_for('main.first_years'))

    # Get form data
    student_id_field = request.form.get('student_id_field')
    email = request.form.get('email')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')

    # Validate required fields
    if not student_id_field or not email or not first_name or not last_name:
        flash('Error: Missing required fields.', 'danger')
        return redirect(url_for('main.first_years'))

    # Check if student_id or email is being changed to a value that already exists (for a different student)
    if student_id_field != student.student_id:
        if Student.query.filter(Student.student_id == student_id_field, Student.id != student.id).first():
            flash('Error: Student ID already exists for another student.', 'danger')
            return redirect(url_for('main.first_years'))

    if email != student.email:
        if Student.query.filter(Student.email == email, Student.id != student.id).first():
            flash('Error: Email already exists for another student.', 'danger')
            return redirect(url_for('main.first_years'))


    # Update student fields
    student.student_id = student_id_field
    student.email = email
    student.first_name = first_name
    student.last_name = last_name
    student.trip_pref_1 = request.form.get('trip_pref_1') or None
    student.trip_pref_2 = request.form.get('trip_pref_2') or None
    student.trip_pref_3 = request.form.get('trip_pref_3') or None
    student.dorm = request.form.get('dorm') or None
    student.athletic_team = request.form.get('athletic_team') or None
    student.gender = request.form.get('gender') or None
    student.hometown = request.form.get('hometown') or None
    water_comfort_val = request.form.get('water_comfort')
    student.water_comfort = int(water_comfort_val) if water_comfort_val else None
    tent_comfort_val = request.form.get('tent_comfort')
    student.tent_comfort = int(tent_comfort_val) if tent_comfort_val else None
    student.notes = request.form.get('notes') or None
    student.poc = request.form.get('poc') == 'true'
    student.fli_international = request.form.get('fli_international') == 'true'

    # Handle trip assignment
    assigned_trip = request.form.get('assigned-trip')
    student.trip_id = int(assigned_trip) if assigned_trip else None

    try:
        db.session.commit()
        flash('Student updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating student: {str(e)}', 'danger')

    return redirect(url_for('main.first_years'))

@main.route('/remove-student', methods=['GET', 'POST'])
@login_required
def remove_student():
   if request.method == 'POST':
       student_id_to_remove = request.form.get('student_id')

       # Make sure the student id was given
       if not student_id_to_remove:
           flash('Error: No student was selected.', 'danger')
           return redirect(url_for('main.first_years'))

       # Find the student in the database
       student = Student.query.get(student_id_to_remove)

       if student:
           try:
               # Delete the student
               db.session.delete(student)
               db.session.commit()
               flash(f'Student {student.first_name} {student.last_name} was removed successfully.', 'success')
           except Exception as e:
               db.session.rollback()
               flash(f'Error: Could not remove student. {str(e)}', 'danger')
       else:
           flash('Error: Student not found.', 'danger')

       return redirect(url_for('main.first_years'))

   return redirect(url_for('main.first_years'))

@main.route('/add-trip', methods=['GET', 'POST'])
@login_required
def add_trip():
    if request.method == 'POST':
        # Get required data from the form
        trip_name = request.form.get('trip_name')
        trip_type = request.form.get('trip_type')
        capacity = request.form.get('capacity')

        # Make sure all required fields are there
        if not trip_name or not trip_type or not capacity:
            flash('Error: One or more required fields (Trip Name, Trip Type, Capacity) are missing.', 'danger')
            return redirect(url_for('main.trips'))

        # Validate capacity is a positive integer
        try:
            capacity = int(capacity)
            if capacity < 1:
                raise ValueError("Capacity must be at least 1")
        except ValueError:
            flash('Error: Capacity must be a positive integer.', 'danger')
            return redirect(url_for('main.trips'))

        # Check if trip name already exists
        if Trip.query.filter_by(trip_name=trip_name).first():
            flash(f'Error: A trip with the name "{trip_name}" already exists.', 'danger')
            return redirect(url_for('main.trips'))

        # Get the data from the checkboxes on the form
        # Returns true if checked, False if unchecked
        water = request.form.get('water') == 'true'
        tent = request.form.get('tent') == 'true'

        # Create a new trip
        new_trip = Trip(
            trip_name=trip_name,
            trip_type=trip_type,
            capacity=capacity,
            address=request.form.get('address'),
            water=water,
            tent=tent
        )

        try:
            # Add to database and save
            db.session.add(new_trip)
            db.session.commit()
            flash('Trip added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error: Could not add trip. {str(e)}', 'danger')

        return redirect(url_for('main.trips'))

    return redirect(url_for('main.trips'))

@main.route('/edit-trip', methods=['POST'])
@login_required
def edit_trip():
    trip_id = request.form.get('trip_id')

    if not trip_id:
        flash('Error: Trip ID is required.', 'danger')
        return redirect(url_for('main.trips'))

    # Query by database primary key (id)
    try:
        trip = Trip.query.get(int(trip_id))
    except (ValueError, TypeError):
        trip = None

    if not trip:
        flash('Error: Trip not found.', 'danger')
        return redirect(url_for('main.trips'))

    trip_name = request.form.get('trip_name')
    trip_type = request.form.get('trip_type')
    capacity = request.form.get('capacity')

    if not trip_name or not trip_type or not capacity:
        flash('Error: Missing required fields.', 'danger')
        return redirect(url_for('main.trips'))

    try:
        capacity = int(capacity)
        if capacity < 1:
            raise ValueError("Capacity must be at least 1")
    except ValueError:
        flash('Error: Capacity must be a positive integer.', 'danger')
        return redirect(url_for('main.trips'))

    if trip_name != trip.trip_name:
        if Trip.query.filter(Trip.trip_name == trip_name, Trip.id != trip.id).first():
            flash(f'Error: A trip with the name "{trip_name}" already exists.', 'danger')
            return redirect(url_for('main.trips'))

    trip.trip_name = trip_name
    trip.trip_type = trip_type
    trip.capacity = capacity
    trip.address = request.form.get('address')
    trip.water = request.form.get('water') == 'true'
    trip.tent = request.form.get('tent') == 'true'

    try:
        db.session.commit()
        flash('Trip updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating trip: {str(e)}', 'danger')

    return redirect(url_for('main.trips'))

@main.route('/remove-trip', methods=['GET', 'POST'])
@login_required
def remove_trip():
   if request.method == 'POST':
       trip_id_to_remove = request.form.get('trip_id')

       # Make sure the trip id was given
       if not trip_id_to_remove:
           flash('Error: No trip was selected.', 'danger')
           return redirect(url_for('main.trips'))

       # Find the trip in the database
       trip = Trip.query.get(trip_id_to_remove)

       if trip:
           try:
               # Delete the trip - student trip placements will be set to NULL automatically
               # by the foreign key constraint (ondelete='SET NULL')
               trip_name = trip.trip_name
               db.session.delete(trip)
               db.session.commit()
               flash(f'Trip {trip_name} was removed successfully. Student placements have been cleared.', 'success')
           except Exception as e:
               db.session.rollback()
               flash(f'Error: Could not remove trip. {str(e)}', 'danger')
       else:
           flash('Error: Trip not found.', 'danger')

       return redirect(url_for('main.trips'))

   return redirect(url_for('main.trips'))


@main.route('/move-student', methods=['POST'])
@login_required
def move_student():
    student_input = request.form.get('student_name', '').strip()
    new_trip_id = request.form.get('new_trip_id')

    # Try to get student by ID first (from dropdown), then fall back to search
    student = None
    if student_input.isdigit():
        student = Student.query.get(int(student_input))

    if not student:
        student = Student.query.filter(
            (Student.student_id == student_input) |
            (Student.first_name.ilike(f"%{student_input}%")) |
            (Student.last_name.ilike(f"%{student_input}%")) |
            ((Student.first_name + ' ' + Student.last_name).ilike(f"%{student_input}%"))
        ).first()

    new_trip = Trip.query.get(new_trip_id)

    if not student or not new_trip:
        return {"success": False, "message": "⚠️ Student or trip not found."}, 400

    student.trip_id = new_trip.id
    db.session.commit()

    # Redirect back to the referring page, default to groups if no referer
    referer = request.referrer
    if referer and ('first-years' in referer or 'groups' in referer):
        return redirect(referer)
    return redirect(url_for('main.groups'))

@main.route('/swap-students', methods=['POST'])
@login_required
def swap_students():
    s1_input = (request.form.get('student1_name') or "").strip()
    s2_input = (request.form.get('student2_name') or "").strip()

    # Try to get students by ID first (from dropdown), then fall back to search
    student1 = None
    if s1_input.isdigit():
        student1 = Student.query.get(int(s1_input))

    if not student1:
        student1 = Student.query.filter(
            (Student.student_id == s1_input) |
            (Student.first_name.ilike(f"%{s1_input}%")) |
            (Student.last_name.ilike(f"%{s1_input}%")) |
            ((Student.first_name + ' ' + Student.last_name).ilike(f"%{s1_input}%"))
        ).first()

    student2 = None
    if s2_input.isdigit():
        student2 = Student.query.get(int(s2_input))

    if not student2:
        student2 = Student.query.filter(
            (Student.student_id == s2_input) |
            (Student.first_name.ilike(f"%{s2_input}%")) |
            (Student.last_name.ilike(f"%{s2_input}%")) |
            ((Student.first_name + ' ' + Student.last_name).ilike(f"%{s2_input}%"))
        ).first()

    if student1 and student2:
        student1.trip_id, student2.trip_id = student2.trip_id, student1.trip_id
        db.session.commit()

    return redirect(url_for('main.groups'))

@main.route('/upload_csv', methods=['POST'])
def upload_csv():
    file = request.files.get('csv_file')
    if not file:
        flash('⚠️ No file selected.', 'danger')
        return redirect(url_for('main.first_years'))

    try:
        stream = StringIO(file.stream.read().decode("utf-8"))
        csv_input = csv.DictReader(stream)

        for row in csv_input:
            def null_if_empty(val):
                v = (val or '').strip()
                return v if v else None

            student_id = null_if_empty(row.get('student_id'))
            first_name = null_if_empty(row.get('first_name'))
            last_name = null_if_empty(row.get('last_name'))
            gender = null_if_empty(row.get('gender'))
            athletic_team = null_if_empty(row.get('athletic_team'))
            hometown = null_if_empty(row.get('hometown'))
            dorm = null_if_empty(row.get('dorm'))
            water_comfort = null_if_empty(row.get('water_comfort'))
            tent_comfort = null_if_empty(row.get('tent_comfort'))
            trip_name = null_if_empty(row.get('trip_name'))
            trip_type = null_if_empty(row.get('trip_type'))
            email = null_if_empty(row.get('email'))
            trip_pref_1 = null_if_empty(row.get('trip_pref_1'))
            trip_pref_2 = null_if_empty(row.get('trip_pref_2'))
            trip_pref_3 = null_if_empty(row.get('trip_pref_3'))
            notes = null_if_empty(row.get('notes'))

            # Validate required fields for student
            if not student_id or not first_name or not last_name or not email:
                continue  # Skip this row if required student fields are missing

            # Handle boolean fields
            poc_value = (row.get('poc') or '').strip().lower()
            poc = poc_value in ['true', '1', 'yes']
            fli_international_value = (row.get('fli_international') or '').strip().lower()
            fli_international = fli_international_value in ['true', '1', 'yes']

            # Handle trip assignment
            trip = None
            if trip_name and trip_type:
                trip = Trip.query.filter_by(trip_name=trip_name).first()
                if not trip:
                    trip = Trip(
                        trip_name=trip_name,
                        trip_type=trip_type,
                        capacity=10,
                        address=None,
                        water=False,
                        tent=False
                    )
                    db.session.add(trip)
                    db.session.flush()

            student = Student.query.filter_by(student_id=student_id).first()
            if not student:
                student = Student(
                    student_id=student_id,
                    first_name=first_name,
                    last_name=last_name,
                    gender=gender,
                    athletic_team=athletic_team,
                    hometown=hometown,
                    dorm=dorm,
                    water_comfort=water_comfort,
                    tent_comfort=tent_comfort,
                    email=email,
                    trip_pref_1=trip_pref_1,
                    trip_pref_2=trip_pref_2,
                    trip_pref_3=trip_pref_3,
                    notes=notes,
                    poc=poc,
                    fli_international=fli_international,
                    trip_id=trip.id if trip else None
                )
                db.session.add(student)
            else:
                student.first_name = first_name
                student.last_name = last_name
                student.gender = gender
                student.athletic_team = athletic_team
                student.hometown = hometown
                student.dorm = dorm
                student.water_comfort = water_comfort
                student.tent_comfort = tent_comfort
                student.email = email
                student.trip_pref_1 = trip_pref_1
                student.trip_pref_2 = trip_pref_2
                student.trip_pref_3 = trip_pref_3
                student.notes = notes
                student.poc = poc
                student.fli_international = fli_international
                student.trip_id = trip.id if trip else None

        db.session.commit()
        flash("CSV uploaded successfully!", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"⚠️ Error processing CSV: {str(e)}", "danger")

    return redirect(url_for('main.first_years'))

@main.route('/sort-students', methods=['POST'])
@login_required
def sort_students_route():
    """Handle the Sort Students button click."""
    try:
        # Run the intelligent sorting algorithm
        stats = sort_students()

        # Commit all changes to database
        db.session.commit()

        # Flash success message with statistics - will show on Groups page
        flash(f'🎯 Sorting completed! {stats["assigned"]}/{stats["total"]} students placed. '
              f'{stats["first_choice_rate"]:.1f}% got first choice, '
              f'{stats["assignment_rate"]:.1f}% total placement rate.', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'⚠️ Sorting failed: {str(e)}', 'danger')

    return redirect(url_for('main.groups'))

def validate_trip(trip):
    """Validate a trip and return validation results."""
    students = trip.students

    validations = {
        'gender_ratio': {'valid': True, 'message': '', 'details': ''},
        'athletic_teams': {'valid': True, 'message': '', 'details': []},
        'roommates': {'valid': True, 'message': '', 'details': []},
        'comfort_levels': {'valid': True, 'message': '', 'details': []},
        'overall_valid': True
    }

    if not students:
        return validations

    male_count = sum(1 for s in students if s.gender and s.gender.lower() == 'male')
    female_count = sum(1 for s in students if s.gender and s.gender.lower() == 'female')
    gender_diff = abs(male_count - female_count)
    if gender_diff > 1:
        validations['gender_ratio']['valid'] = False
        validations['gender_ratio']['message'] = f"{male_count} Male, {female_count} Female"
        validations['gender_ratio']['details'] = f"Gender ratio off by {gender_diff}"
        validations['overall_valid'] = False
    else:
        validations['gender_ratio']['message'] = f"{male_count} Male, {female_count} Female"

    athletic_teams = {}
    for student in students:
        if student.athletic_team and student.athletic_team.lower() not in ['n/a', 'none', '', 'null']:
            team = student.athletic_team
            athletic_teams.setdefault(team, []).append(f"{student.first_name} {student.last_name}")

    duplicate_teams = {team: names for team, names in athletic_teams.items() if len(names) > 1}
    if duplicate_teams:
        validations['athletic_teams']['valid'] = False
        for team, names in duplicate_teams.items():
            validations['athletic_teams']['details'].append(f"{', '.join(names)} share team ({team}).")
        validations['overall_valid'] = False

    dorms = {}
    for student in students:
        if student.dorm:
            dorms.setdefault(student.dorm, []).append(f"{student.first_name} {student.last_name}")

    duplicate_dorms = {d: n for d, n in dorms.items() if len(n) > 1}
    if duplicate_dorms:
        validations['roommates']['valid'] = False
        for dorm, names in duplicate_dorms.items():
            validations['roommates']['details'].append(f"{', '.join(names)} share dorm ({dorm}).")
        validations['overall_valid'] = False

    if trip.water:
        low_water = [f"{s.first_name} {s.last_name}" for s in students if s.water_comfort and int(s.water_comfort) <= 2]
        if low_water:
            validations['comfort_levels']['valid'] = False
            validations['comfort_levels']['details'].append(f"Low water comfort: {', '.join(low_water)}")
            validations['overall_valid'] = False

    if trip.tent:
        low_tent = [f"{s.first_name} {s.last_name}" for s in students if s.tent_comfort and int(s.tent_comfort) <= 2]
        if low_tent:
            validations['comfort_levels']['valid'] = False
            validations['comfort_levels']['details'].append(f"Low tent comfort: {', '.join(low_tent)}")
            validations['overall_valid'] = False

    return validations