from flask import Blueprint, jsonify, request
from models import Student, Trip, db
from sort import sort_students
from flask_login import login_required
from static.utils.decorators import manager_required, admin_required, student_required
import traceback

api = Blueprint('api', __name__, url_prefix='/api')

# Health check
@api.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'COOT Compass API running'})

# Get all students
@api.route('/students', methods=['GET'])
@admin_required
def get_students():
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

# Get all trips
@api.route('/trips', methods=['GET'])
@admin_required
def get_trips():
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

# Move student to trip
@api.route('/move-student', methods=['POST'])
@admin_required
def move_student():
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
            message = f'{student.first_name} {student.last_name} moved from {old_trip_name} to {new_trip.trip_name}'
        else:
            student.trip_id = None
            message = f'{student.first_name} {student.last_name} removed from {old_trip_name}'

        db.session.commit()

        return jsonify({
            'success': True,
            'message': message
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Swap students
@api.route('/swap-students', methods=['POST'])
@admin_required
def swap_students():
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

        return jsonify({
            'success': True,
            'message': f'Swapped {student1.first_name} {student1.last_name} ({trip1_name}) with {student2.first_name} {student2.last_name} ({trip2_name})'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Sort students
@api.route('/sort-students', methods=['POST'])
@admin_required
def sort_students_api():
    try:
        # Run the existing sort function
        result = sort_students()
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Students sorted successfully',
            'stats': result
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
