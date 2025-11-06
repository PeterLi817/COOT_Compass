from flask import Blueprint, render_template, redirect, url_for, request, flash
from models import Student, Trip, db
from flask_login import login_required

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
    # Add validation data and capacity info to each trip
    for trip in trips:
        trip.validations = validate_trip(trip)
        # Calculate capacity information
        trip.current_students = len(trip.students)
        trip.has_open_slots = trip.current_students < trip.capacity
        trip.open_slots_count = trip.capacity - trip.current_students
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

def validate_trip(trip):
    """Validate a trip and return validation results."""
    students = trip.students

    # Initialize validation results
    validations = {
        'gender_ratio': {'valid': True, 'message': '', 'details': ''},
        'athletic_teams': {'valid': True, 'message': '', 'details': []},
        'roommates': {'valid': True, 'message': '', 'details': []},
        'comfort_levels': {'valid': True, 'message': '', 'details': []},
        'overall_valid': True
    }

    if not students:
        return validations

    # 1. Gender Ratio Check - bad if difference is more than 1
    male_count = sum(1 for s in students if s.gender and s.gender.lower() == 'male')
    female_count = sum(1 for s in students if s.gender and s.gender.lower() == 'female')
    other_count = len(students) - male_count - female_count

    gender_diff = abs(male_count - female_count)
    if gender_diff > 1:
        validations['gender_ratio']['valid'] = False
        validations['gender_ratio']['message'] = f"{male_count} Male, {female_count} Female"
        validations['gender_ratio']['details'] = f"Gender ratio is off by {gender_diff}"
        validations['overall_valid'] = False
    else:
        validations['gender_ratio']['message'] = f"{male_count} Male, {female_count} Female"

    # 2. Athletic Teams Check - students shouldn't be on the same athletic teams
    athletic_teams = {}
    for student in students:
        if student.athletic_team and student.athletic_team.lower() != 'n/a':
            team = student.athletic_team
            if team not in athletic_teams:
                athletic_teams[team] = []
            athletic_teams[team].append(f"{student.first_name} {student.last_name}")

    # Check for duplicates
    duplicate_teams = {team: names for team, names in athletic_teams.items() if len(names) > 1}
    if duplicate_teams:
        validations['athletic_teams']['valid'] = False
        validations['athletic_teams']['details'] = []
        for team, names in duplicate_teams.items():
            validations['athletic_teams']['details'].append(f"{', '.join(names)} are on the same athletic team ({team}).")
        validations['overall_valid'] = False

    # 3. Roommates Check - people should not live in the same rooms (dorm)
    dorms = {}
    for student in students:
        if student.dorm:
            dorm = student.dorm
            if dorm not in dorms:
                dorms[dorm] = []
            dorms[dorm].append(f"{student.first_name} {student.last_name}")

    # Check for duplicates
    duplicate_dorms = {dorm: names for dorm, names in dorms.items() if len(names) > 1}
    if duplicate_dorms:
        validations['roommates']['valid'] = False
        validations['roommates']['details'] = []
        for dorm, names in duplicate_dorms.items():
            validations['roommates']['details'].append(f"{', '.join(names)} are roommates (live in {dorm}).")
        validations['overall_valid'] = False

    # 4. Comfort Levels Check - if people are <=2 on tent/water comfort, they shouldn't be on a tent/water trip
    if trip.water:
        low_water_comfort = [
            f"{s.first_name} {s.last_name}"
            for s in students
            if s.water_comfort is not None and s.water_comfort <= 2
        ]
        if low_water_comfort:
            validations['comfort_levels']['valid'] = False
            validations['comfort_levels']['details'].append(
                f"Water trip with low comfort: {', '.join(low_water_comfort)} have water comfort <= 2."
            )
            validations['overall_valid'] = False

    if trip.tent:
        low_tent_comfort = [
            f"{s.first_name} {s.last_name}"
            for s in students
            if s.tent_comfort is not None and s.tent_comfort <= 2
        ]
        if low_tent_comfort:
            validations['comfort_levels']['valid'] = False
            validations['comfort_levels']['details'].append(
                f"Tent trip with low comfort: {', '.join(low_tent_comfort)} have tent comfort <= 2."
            )
            validations['overall_valid'] = False

    return validations