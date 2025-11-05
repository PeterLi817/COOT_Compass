from flask import Blueprint, render_template, redirect, url_for
from models import Student, Trip
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
    # Add validation data and capacity info to each trip
    for trip in trips:
        trip.validations = validate_trip(trip)
        # Calculate capacity information
        trip.current_students = len(trip.students)
        trip.has_open_slots = trip.current_students < trip.capacity
        trip.open_slots_count = trip.capacity - trip.current_students
    return render_template('groups.html', trips=trips)

@main.route('/settings')
@login_required
def settings():
    return render_template('settings.html')



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
