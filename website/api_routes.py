"""API routes for COOT Compass.

This module provides RESTful API endpoints for managing students, trips, users,
and application settings. All endpoints return JSON responses and require
appropriate authentication and authorization based on user roles.
"""

import io
import csv

from flask import Blueprint, jsonify, request, flash
from flask_login import current_user

from website import db
from .models import AppSettings, Student, Trip, User
from .static.utils.decorators import manager_required, admin_required
from .sort import sort_students

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/health', methods=['GET'])
def health_check():
    """Check the health status of the API.

    Returns:
        dict: A JSON response indicating the API is running.
    """
    return jsonify({'status': 'healthy', 'message': 'COOT Compass API running'})

@api.route('/students', methods=['GET'])
@admin_required
def get_students():
    """Retrieve all students from the database.

    Returns a JSON response containing all student records with their
    associated trip information and preferences.

    Returns:
        dict: JSON response with success status and list of students.
            On error, returns error message with 500 status code.
    """
    try:
        students = Student.query.all()
        return jsonify({
            'success': True,
            'students': [{
                'id': s.id,
                'student_id': s.student_id,
                'first_name': s.first_name,
                'last_name': s.last_name,
                'gender': s.gender,
                'athletic_team': s.athletic_team,
                'dorm': s.dorm,
                'trip_id': s.trip_id,
                'trip_name': s.trip.trip_name if s.trip else None,
                'trip_pref_1': s.trip_pref_1,
                'trip_pref_2': s.trip_pref_2,
                'trip_pref_3': s.trip_pref_3
            } for s in students]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api.route('/trips', methods=['GET'])
@admin_required
def get_trips():
    """Retrieve all trips from the database.

    Returns a JSON response containing all trip records with their
    capacity information, current student count, and assigned students.

    Returns:
        dict: JSON response with success status and list of trips.
            On error, returns error message with 500 status code.
    """
    try:
        trips = Trip.query.all()
        return jsonify({
            'success': True,
            'trips': [{
                'id': t.id,
                'trip_name': t.trip_name,
                'trip_type': t.trip_type,
                'capacity': t.capacity,
                'current_count': len(t.students),
                'available_spots': t.capacity - len(t.students),
                'water': t.water,
                'tent': t.tent,
                'students': [{
                    'id': s.id,
                    'first_name': s.first_name,
                    'last_name': s.last_name,
                    'student_id': s.student_id
                } for s in t.students]
            } for t in trips]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api.route('/move-student', methods=['POST'])
@admin_required
def move_student():
    """Move a student to a different trip or remove them from their current trip.

    Expects JSON data with 'student_id' and optionally 'new_trip_id'.
    If 'new_trip_id' is None or not provided, the student is removed from
    their current trip.

    Args (JSON):
        student_id (int): The ID of the student to move.
        new_trip_id (int, optional): The ID of the destination trip.

    Returns:
        dict: JSON response with success status and operation message.
            Returns 400 if trip is at capacity, 404 if student/trip not found,
            or 500 on error.
    """
    try:
        data = request.get_json()
        student_id = data.get('student_id')
        new_trip_id = data.get('new_trip_id')

        student = Student.query.get_or_404(student_id)
        old_trip_name = student.trip.trip_name if student.trip else "No Trip"

        if new_trip_id:
            new_trip = Trip.query.get_or_404(new_trip_id)

            # Check capacity
            if len(new_trip.students) >= new_trip.capacity:
                return jsonify({
                    'success': False,
                    'error': f'Trip {new_trip.trip_name} is at full capacity'
                }), 400

            student.trip_id = new_trip_id
            message = (
                f'{student.first_name} {student.last_name} moved from '
                f'{old_trip_name} to {new_trip.trip_name}'
            )
        else:
            student.trip_id = None
            message = (
                f'{student.first_name} {student.last_name} removed from '
                f'{old_trip_name}'
            )

        db.session.commit()

        return jsonify({
            'success': True,
            'message': message
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@api.route('/swap-students', methods=['POST'])
@admin_required
def swap_students():
    """Swap the trip assignments of two students.

    Expects JSON data with 'student1_id' and 'student2_id'. The students
    will exchange their current trip assignments.

    Args (JSON):
        student1_id (int): The ID of the first student.
        student2_id (int): The ID of the second student.

    Returns:
        dict: JSON response with success status and swap confirmation message.
            Returns 404 if either student is not found, or 500 on error.
    """
    try:
        data = request.get_json()
        student1_id = data.get('student1_id')
        student2_id = data.get('student2_id')

        student1 = Student.query.get_or_404(student1_id)
        student2 = Student.query.get_or_404(student2_id)

        # Get current trip names for message
        trip1_name = student1.trip.trip_name if student1.trip else "No Trip"
        trip2_name = student2.trip.trip_name if student2.trip else "No Trip"

        # Swap assignments
        temp_trip_id = student1.trip_id
        student1.trip_id = student2.trip_id
        student2.trip_id = temp_trip_id

        db.session.commit()

        message = (
            f'Swapped {student1.first_name} {student1.last_name} ({trip1_name}) '
            f'with {student2.first_name} {student2.last_name} ({trip2_name})'
        )

        return jsonify({
            'success': True,
            'message': message
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@api.route('/get-users')
@admin_required
def get_users():
    """Retrieve all users from the database.

    Returns a JSON response containing all user records with their
    email, name, and role information.

    Returns:
        dict: JSON response with list of users.
            Returns 500 status code on error.
    """
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

@api.route('/settings/show_trips', methods=['GET'])
@admin_required
def api_get_show_trips():
    """Get the current setting for whether trips are visible to students.

    Returns:
        dict: JSON response with the current 'show_trips_to_students' setting value.
    """
    settings = AppSettings.get()
    return jsonify({'show_trips_to_students': settings.show_trips_to_students})

@api.route('/settings/toggle_show_trips', methods=['POST'])
@admin_required
def api_toggle_show_trips():
    """Toggle or set the visibility of trips to students.

    Expects optional JSON data with 'value' (boolean). If 'value' is provided,
    sets the setting to that value. Otherwise, toggles the current value.

    Args (JSON, optional):
        value (bool, optional): The desired value for the setting.

    Returns:
        dict: JSON response with success status and updated setting value.
    """
    data = request.get_json() or {}
    value = data.get('value')

    settings = AppSettings.get()
    if value is None:
        settings.show_trips_to_students = not settings.show_trips_to_students
    else:
        settings.show_trips_to_students = bool(value)

    db.session.commit()
    return jsonify({'success': True, 'show_trips_to_students': settings.show_trips_to_students})

@api.route('/process_matched_csv', methods=['POST'])
@admin_required
def process_matched_csv():
    """Process a CSV file to import or update student data.

    Accepts a CSV file and form data mapping CSV columns to database fields.
    Supports two import modes: 'update' (updates existing students) or
    'add' (only adds new students). Can also create trips if trip_name
    and trip_type are provided.

    Args (form data):
        csv_file: The uploaded CSV file.
        importMode: Either 'update' or 'add'.
        Column mappings: Form fields mapping CSV column names to database fields.

    Returns:
        dict: JSON response with success status, counts of added/updated/skipped
            records, and any errors encountered. Returns 400 if no file provided
            or CSV is empty, or 500 on error.
    """
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
                    if db_field == "trip_type":
                        trip_type = value
                        continue
                    if db_field in valid_fields:
                        # Handle boolean fields (nullable)
                        if db_field in ['poc', 'fli_international']:
                            if value:
                                mapped[db_field] = value.lower() in ['true', '1', 'yes', 'y']
                            else:
                                mapped[db_field] = None
                        # Handle integer fields (nullable)
                        elif db_field in ['water_comfort', 'tent_comfort']:
                            if value and value.isdigit():
                                mapped[db_field] = int(value)
                            else:
                                mapped[db_field] = None
                        else:
                            mapped[db_field] = value if value else None

                student_id = mapped.get("student_id")
                if not student_id:
                    errors.append(f"Row {idx}: Missing student_id (required)")
                    skipped += 1
                    continue

                # Validate required fields for new students
                if import_mode != "update":
                    if not mapped.get('first_name'):
                        errors.append(f"Row {idx}: Missing first_name (required)")
                        skipped += 1
                        continue
                    if not mapped.get('last_name'):
                        errors.append(f"Row {idx}: Missing last_name (required)")
                        skipped += 1
                        continue
                    if not mapped.get('email'):
                        errors.append(f"Row {idx}: Missing email (required)")
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

@api.route('/process_matched_trips_csv', methods=['POST'])
@admin_required
def process_matched_trips_csv():
    """Process a CSV file to import or update trip data.

    Accepts a CSV file and form data mapping CSV columns to database fields.
    Supports two import modes: 'update' (updates existing trips) or
    'add' (only adds new trips).

    Args (form data):
        csv_file: The uploaded CSV file.
        importMode: Either 'update' or 'add'.
        Column mappings: Form fields mapping CSV column names to database fields.

    Returns:
        dict: JSON response with success status, counts of added/updated/skipped
            records, and any errors encountered. Returns 400 if no file provided
            or CSV is empty, or 500 on error.
    """
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
            'trip_name', 'trip_type', 'capacity', 'address', 'water', 'tent'
        }

        added, updated, skipped = 0, 0, 0
        errors = []

        for idx, row in enumerate(rows, start=2):
            try:
                mapped = {}

                for csv_col, db_field in column_map.items():
                    value = (row.get(csv_col) or "").strip()

                    if db_field in valid_fields:
                        if db_field in ['water', 'tent']:
                            # Handle boolean fields with defaults
                            if value:
                                mapped[db_field] = value.lower() in ['true', '1', 'yes', 'y']
                            # If empty, don't set it - let the model default handle it
                        elif db_field == 'capacity':
                            # Handle integer field (required, non-nullable)
                            if value and value.isdigit():
                                mapped[db_field] = int(value)
                            # Don't set to None - will be validated or defaulted later
                        else:
                            mapped[db_field] = value if value else None

                trip_name = mapped.get("trip_name")
                if not trip_name:
                    errors.append(f"Row {idx}: Missing trip_name")
                    skipped += 1
                    continue

                existing = Trip.query.filter_by(trip_name=trip_name).first()

                if import_mode == "update" and existing:
                    for key, val in mapped.items():
                        setattr(existing, key, val)
                    updated += 1

                elif not existing:
                    # Ensure required fields are present
                    if not mapped.get('trip_type'):
                        errors.append(f"Row {idx}: Missing trip_type (required)")
                        skipped += 1
                        continue
                    if not mapped.get('capacity'):
                        errors.append(f"Row {idx}: Missing or invalid capacity (required)")
                        skipped += 1
                        continue

                    new_trip = Trip(**mapped)
                    db.session.add(new_trip)
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

@api.route('/update-user-role', methods=['POST'])
@manager_required
def update_user_role():
    """Update a user's role in the system.

    Expects JSON data with 'email' and 'role'. Valid roles are:
    'admin_manager', 'admin', 'student', 'none' (or None).

    Args (JSON):
        email (str): The email of the user to update.
        role (str): The new role for the user. Can be 'admin_manager', 'admin',
            'student', 'none', or None.

    Returns:
        dict: JSON response with success status. Returns 400 for invalid input,
            403 if attempting to change own admin_manager role, 404 if user not
            found, or 500 on error.
    """
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
        if (
            user.email == current_user.email
            and current_user.role == 'admin_manager'
            and new_role != 'admin_manager'
        ):
            flash('Cannot change your own admin_manager role', 'danger')
            return jsonify({'success': False}), 403

        # Update role
        user.role = new_role
        db.session.commit()

        role_display = new_role if new_role else 'None'
        flash(
            f"Successfully updated {user.first_name} "
            f"{user.last_name}'s role to {role_display}",
            'success'
        )
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating user role: {str(e)}', 'danger')
        return jsonify({'success': False}), 500

@api.route('/sort-students', methods=['POST'])
@admin_required
def sort_students_api():
    """Automatically sort and assign students to trips based on preferences.

    Optionally accepts custom sorting criteria. Uses the COOT sorting algorithm
    to assign students to trips while respecting constraints like capacity,
    gender balance, dorm assignments, and athletic teams.

    Args (JSON, optional):
        criteria (list, optional): Custom sorting criteria to use.

    Returns:
        dict: JSON response with success status, completion message, and
            sorting statistics. Returns 400 on error.
    """
    try:
        data = request.get_json(silent=True) or {}
        criteria = data.get('criteria')
        if criteria:
            stats = sort_students(custom_criteria=criteria)
        else:
            stats = sort_students()
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Sorting completed.',
            'stats': stats
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
