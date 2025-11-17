from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, Response, send_file
from models import Student, Trip, db, User
from flask_login import login_required, current_user
import csv
import io
from sort import sort_students
import json
from static.utils.decorators import manager_required, admin_required, student_required
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

main = Blueprint('main', __name__)

@main.route('/settings')
@admin_required
def settings():
    return render_template('settings.html',current_user=current_user)

@main.route('/get-users')
@admin_required
def get_users():
    """API endpoint to fetch all users."""
    try:
        users = User.query.all()
        users_data = [
            {
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role
            }
            for user in users
        ]
        return jsonify({'users': users_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main.route('/student_view')
@student_required
def student_view():
    return render_template('student_view.html', current_user=current_user, now=datetime.now())

@main.route('/no_access')
@login_required
def no_access():
    return render_template('no_view.html', current_user=current_user, now=datetime.now())

@main.route('/trips')
@admin_required
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
@admin_required
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
@admin_required
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
@admin_required
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
    student_db_id = request.form.get('student_db_id')

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

    # Get form data - check for student_id_field first (edit mode), then fall back to student_id (add mode)
    student_id_field = request.form.get('student_id_field') or request.form.get('student_id')
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
@admin_required
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
@admin_required
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
@admin_required
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
@admin_required
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
@admin_required
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
@admin_required
def upload_csv():
    file = request.files.get('csv_file')
    if not file:
        flash('⚠️ No file selected.', 'danger')
        return redirect(url_for('main.groups'))

    try:
        stream = io.StringIO(file.stream.read().decode("utf-8"))
        csv_input = csv.DictReader(stream)
        
        # Normalize column names (case-insensitive, strip whitespace)
        def normalize_key(key):
            return key.strip().lower().replace(' ', '_').replace('-', '_') if key else ''
        
        # Create a mapping of normalized column names to actual column names
        fieldnames = csv_input.fieldnames or []
        column_map = {normalize_key(fn): fn for fn in fieldnames}
        
        def get_value(row, possible_keys):
            """Get value from row using possible normalized keys"""
            for key in possible_keys:
                normalized = normalize_key(key)
                if normalized in column_map:
                    actual_key = column_map[normalized]
                    return (row.get(actual_key) or '').strip()
            return ''

        added_count = 0
        updated_count = 0
        skipped_count = 0
        
        for row in csv_input:
            # Try multiple possible column name variations
            student_id = get_value(row, ['student_id', 'Student ID', 'student id', 'ID'])
            first_name = get_value(row, ['first_name', 'First Name', 'first name', 'First', 'first'])
            last_name = get_value(row, ['last_name', 'Last Name', 'last name', 'Last', 'last'])
            email = get_value(row, ['email', 'Email', 'EMAIL', 'e-mail'])
            gender = get_value(row, ['gender', 'Gender', 'GENDER', 'sex', 'Sex'])
            team = get_value(row, ['athletic_team', 'Athletic Team', 'athletic team', 'team', 'Team', 'sport'])
            hometown = get_value(row, ['hometown', 'Hometown', 'Hometown', 'city', 'City'])
            dorm = get_value(row, ['dorm', 'Dorm', 'DORM', 'residence', 'Residence'])
            water_comfort = get_value(row, ['water_comfort', 'Water Comfort', 'water comfort', 'water'])
            tent_comfort = get_value(row, ['tent_comfort', 'Tent Comfort', 'tent comfort', 'tent'])
            trip_name = get_value(row, ['trip_name', 'Trip Name', 'trip name', 'Trip', 'trip'])
            trip_type = get_value(row, ['trip_type', 'Trip Type', 'trip type', 'Type', 'type'])

            if not student_id or not first_name or not last_name or not email:
                skipped_count += 1
                continue

            trip = None
            if trip_name:
                trip = Trip.query.filter_by(trip_name=trip_name).first()
                if not trip and trip_type:
                    trip = Trip(
                        trip_name=trip_name,
                        trip_type=trip_type,
                        capacity=10,
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
                    gender=gender if gender else None,
                    athletic_team=team if team else None,
                    hometown=hometown if hometown else None,
                    dorm=dorm if dorm else None,
                    water_comfort=water_comfort if water_comfort else None,
                    tent_comfort=tent_comfort if tent_comfort else None,
                    email=email,
                    trip_id=trip.id if trip else None
                )
                db.session.add(student)
                added_count += 1
            else:
                student.first_name = first_name
                student.last_name = last_name
                student.gender = gender if gender else None
                student.athletic_team = team if team else None
                student.hometown = hometown if hometown else None
                student.dorm = dorm if dorm else None
                student.water_comfort = water_comfort if water_comfort else None
                student.tent_comfort = tent_comfort if tent_comfort else None
                student.email = email
                student.trip_id = trip.id if trip else None
                updated_count += 1

        db.session.commit()
        flash(f"CSV uploaded successfully! Added: {added_count}, Updated: {updated_count}, Skipped: {skipped_count}", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"⚠️ Error processing CSV: {str(e)}", "danger")

    return redirect(url_for('main.groups'))

@main.route('/process_matched_csv', methods=['POST'])
@login_required
def process_matched_csv():
    try:
        file = request.files.get("csv_file")
        import_mode = request.form.get("importMode")

        if not file:
            return jsonify({"success": False, "message": "No CSV uploaded."}), 400

        stream = io.StringIO(file.stream.read().decode("utf-8"))
        csv_input = csv.DictReader(stream)
        rows = list(csv_input)

        if not rows:
            return jsonify({"success": False, "message": "CSV is empty."}), 400

        column_map = {
            csv_col: request.form.get(csv_col)
            for csv_col in request.form
            if csv_col not in ["csv_file", "importMode"] and request.form.get(csv_col)
        }

        valid_fields = {
            'student_id', 'first_name', 'last_name', 'email', 'trip_id',
            'trip_pref_1', 'trip_pref_2', 'trip_pref_3', 'dorm',
            'athletic_team', 'gender', 'notes', 'water_comfort',
            'tent_comfort', 'hometown', 'poc', 'fli_international'
        }

        added, updated, skipped = 0, 0, 0
        errors = []

        for idx, row in enumerate(rows, start=2):
            try:
                mapped = {}
                trip_name = None
                trip_type = None

                for csv_col, db_field in column_map.items():
                    value = (row.get(csv_col) or "").strip()

                    if db_field == "trip_name":
                        trip_name = value
                        continue
                    elif db_field == "trip_type":
                        trip_type = value
                        continue
                    elif db_field in valid_fields:
                        mapped[db_field] = value if value else None

                student_id = mapped.get("student_id")
                if not student_id:
                    errors.append(f"Row {idx}: Missing student_id")
                    skipped += 1
                    continue

                if trip_name:
                    trip = Trip.query.filter_by(trip_name=trip_name).first()
                    if not trip and trip_type:
                        trip = Trip(
                            trip_name=trip_name,
                            trip_type=trip_type,
                            capacity=10,
                            water=False,
                            tent=False
                        )
                        db.session.add(trip)
                        db.session.flush()
                    mapped["trip_id"] = trip.id if trip else None

                existing = Student.query.filter_by(student_id=student_id).first()

                if import_mode == "update" and existing:
                    for key, val in mapped.items():
                        setattr(existing, key, val)
                    updated += 1

                elif not existing:
                    new_student = Student(**mapped)
                    db.session.add(new_student)
                    added += 1

                else:
                    skipped += 1

            except Exception as e:
                errors.append(f"Row {idx}: {str(e)}")
                skipped += 1
                continue

        db.session.commit()

        return jsonify({
            "success": True,
            "added": added,
            "updated": updated,
            "skipped": skipped,
            "errors": errors[:10]
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

@main.route('/export_csv')
@login_required
def export_csv():
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        'Trip Name', 'Trip Type', 'Student ID', 'First Name', 'Last Name',
        'Gender', 'Athletic Team', 'Dorm', 'Hometown'
    ])

    trips = sorted(
        Trip.query.all(),
        key=lambda t: int(''.join(filter(str.isdigit, t.trip_name)) or 0)
    )

    for trip in trips:
        for student in trip.students:
            writer.writerow([
                trip.trip_name,
                trip.trip_type,
                student.student_id,
                student.first_name,
                student.last_name,
                student.gender or '',
                student.athletic_team or '',
                student.dorm or '',
                student.hometown or ''
            ])

    output.seek(0)
    filename = f"trip_rosters_{datetime.now().strftime('%b-%d-%Y_%I-%M%p')}.csv"

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@main.route('/export_pdf')
@login_required
def export_pdf():
    try:
        pdf_buffer = io.BytesIO()
        p = canvas.Canvas(pdf_buffer, pagesize=letter)
        width, height = letter

        trips = sorted(
            Trip.query.all(),
            key=lambda t: int(''.join(filter(str.isdigit, t.trip_name)) or 0)
        )

        first_page = True
        for trip in trips:
            if not first_page:
                p.showPage()
            first_page = False

            y = height - 80

            p.setFont("Helvetica-Bold", 16)
            p.drawString(150, height - 50, "Trip Roster")

            p.setFont("Helvetica-Bold", 12)
            p.drawString(50, y, f"Trip: {trip.trip_name} ({trip.trip_type})")
            y -= 20

            p.setFont("Helvetica", 10)
            p.drawString(70, y, f"Capacity: {len(trip.students)}/{trip.capacity}")
            y -= 20

            p.setFont("Helvetica-Bold", 11)
            p.drawString(70, y, "Students:")
            y -= 15

            p.setFont("Helvetica", 10)

            for student in trip.students:
                line = (
                    f"- {student.first_name} {student.last_name}, "
                    f"{student.gender or ''}, "
                    f"{student.athletic_team or ''}, "
                    f"{student.dorm or ''}"
                )
                p.drawString(90, y, line)
                y -= 15

                if y < 80:
                    p.showPage()
                    y = height - 80

        p.save()
        pdf_buffer.seek(0)

        filename = f"trip_rosters_{datetime.now().strftime('%b-%d-%Y_%I-%M%p')}.pdf"
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype="application/pdf"
        )

    except Exception as e:
        return f"Error generating PDF: {str(e)}", 500

@main.route('/download_sample_csv')
@login_required
def download_sample_csv():
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        'student_id', 'first_name', 'last_name', 'email', 'gender',
        'athletic_team', 'dorm', 'hometown',
        'water_comfort', 'tent_comfort', 'trip_name', 'trip_type'
    ])

    sample_data = [
        ['S001', 'John', 'Smith', 'john.smith@colby.edu', 'Male', 'Soccer', 'Dana', 'Portland ME', '4', '5', 'Trip 1', 'backpacking'],
        ['S002', 'Jane', 'Doe', 'jane.doe@colby.edu', 'Female', 'Swimming', 'West', 'Boston MA', '5', '4', 'Trip 2', 'canoeing']
    ]

    for row in sample_data:
        writer.writerow(row)

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={"Content-Disposition": "attachment; filename=sample_students.csv"}
    )


@main.route('/sort-students', methods=['POST'])
@admin_required
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

@main.route('/update-user-role', methods=['POST'])
@manager_required
def update_user_role():
    """API endpoint to update a user's role."""
    try:
        data = request.get_json()
        email = data.get('email')
        new_role = data.get('role')

        if not email:
            flash('Missing email', 'danger')
            return jsonify({'success': False}), 400

        # Validate role
        valid_roles = ['admin_manager', 'admin', 'student', 'none', None]
        if new_role not in valid_roles:
            flash('Invalid role', 'danger')
            return jsonify({'success': False}), 400

        # Convert string 'none' to None
        if new_role == 'none':
            new_role = None

        # Find user
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('User not found', 'danger')
            return jsonify({'success': False}), 404

        # Prevent self-demotion from admin_manager
        if user.email == current_user.email and current_user.role == 'admin_manager' and new_role != 'admin_manager':
            flash('Cannot change your own admin_manager role', 'danger')
            return jsonify({'success': False}), 403

        # Update role
        user.role = new_role
        db.session.commit()

        role_display = new_role if new_role else 'None'
        flash(f'Successfully updated {user.first_name} {user.last_name}\'s role to {role_display}', 'success')
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating user role: {str(e)}', 'danger')
        return jsonify({'success': False}), 500

@main.route('/clear-databases', methods=['POST'])
@manager_required
def clear_databases():
    try:
        # Delete all students and trips
        num_students = Student.query.delete()
        num_trips = Trip.query.delete()

        # Delete users with role 'student' or None
        from models import User
        num_users = User.query.filter((User.role == 'student') | (User.role == None)).delete(synchronize_session=False)

        db.session.commit()
        flash(f'🗑️ Cleared databases: {num_students} students, {num_trips} trips, and {num_users} users removed.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'⚠️ Error clearing databases: {str(e)}', 'danger')
    return redirect(url_for('main.settings'))

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