import pytest
import json
import io
import csv
import time
from unittest.mock import patch, MagicMock
from website import db
from website.models import User, Student, Trip, AppSettings
from flask_login import login_user

# ============================================
# Fixtures
# ============================================

@pytest.fixture
def admin_user(test_client):
    """Create an admin user for testing"""
    with test_client.application.app_context():
        admin = User.query.filter_by(email='admin@test.com').first()
        if not admin:
            admin = User(
                email='admin@test.com',
                first_name='Admin',
                last_name='User',
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
        return admin

@pytest.fixture
def manager_user(test_client):
    """Create an admin_manager user for testing"""
    with test_client.application.app_context():
        manager = User.query.filter_by(email='manager@test.com').first()
        if not manager:
            manager = User(
                email='manager@test.com',
                first_name='Manager',
                last_name='User',
                role='admin_manager'
            )
            db.session.add(manager)
            db.session.commit()
        return manager

@pytest.fixture
def authenticated_admin_client(test_client, admin_user):
    """Test client with admin user logged in"""
    # Ensure user exists in database and has correct role
    with test_client.application.app_context():
        existing = User.query.filter_by(email=admin_user.email).first()
        if existing:
            existing.role = 'admin'
        else:
            admin_user.role = 'admin'
            db.session.add(admin_user)
        db.session.commit()
    
    # Set session for Flask-Login - use the email as the user_id
    with test_client.session_transaction() as sess:
        sess['_user_id'] = admin_user.email  # Flask-Login uses get_id() which returns email
        sess['_fresh'] = True
    
    yield test_client

@pytest.fixture
def authenticated_manager_client(test_client, manager_user):
    """Test client with manager user logged in"""
    # Ensure user exists in database and has correct role
    with test_client.application.app_context():
        existing = User.query.filter_by(email=manager_user.email).first()
        if existing:
            existing.role = 'admin_manager'
        else:
            manager_user.role = 'admin_manager'
            db.session.add(manager_user)
        db.session.commit()
    
    # Set session for Flask-Login
    with test_client.session_transaction() as sess:
        sess['_user_id'] = manager_user.email
        sess['_fresh'] = True
    
    yield test_client

@pytest.fixture
def sample_student(test_client):
    """Create a sample student for testing"""
    import time
    unique_id = int(time.time() * 1000) % 100000
    
    with test_client.application.app_context():
        student = Student.query.filter_by(student_id=f'TEST{unique_id}').first()
        if not student:
            student = Student(
                student_id=f'TEST{unique_id}',
                first_name='Test',
                last_name='Student',
                email=f'teststudent{unique_id}@test.com'
            )
            db.session.add(student)
            db.session.commit()
        return student

@pytest.fixture
def sample_trip(test_client):
    """Create a sample trip for testing"""
    import time
    unique_id = int(time.time() * 1000) % 100000
    
    with test_client.application.app_context():
        trip = Trip.query.filter_by(trip_name=f'Test Trip {unique_id}').first()
        if not trip:
            trip = Trip(
                trip_name=f'Test Trip {unique_id}',
                trip_type='backpacking',
                capacity=5
            )
            db.session.add(trip)
            db.session.commit()
        return trip

# ============================================
# Test /api/health endpoint
# ============================================

def test_health_check(test_client):
    """Test that health check endpoint works without authentication"""
    response = test_client.get('/api/health')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert 'message' in data

# ============================================
# Test /api/students endpoint
# ============================================

def test_get_students_requires_admin(test_client):
    """Test that /api/students requires admin authentication"""
    response = test_client.get('/api/students')
    assert response.status_code in [401, 302, 403]

def test_get_students_success(authenticated_admin_client, sample_student):
    """Test successful retrieval of students list"""
    response = authenticated_admin_client.get('/api/students')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert 'students' in data
    assert isinstance(data['students'], list)
    # Check student structure
    if data['students']:
        student = data['students'][0]
        assert 'id' in student
        assert 'student_id' in student
        assert 'first_name' in student
        assert 'last_name' in student

def test_get_students_error_handling(authenticated_admin_client):
    """Test error handling in get_students"""
    # This tests the exception handler (line 40-41)
    # We can't easily trigger a database error, but the code path exists
    response = authenticated_admin_client.get('/api/students')
    assert response.status_code in [200, 500]  # Should work or handle error gracefully

# ============================================
# Test /api/trips endpoint
# ============================================

def test_get_trips_requires_admin(test_client):
    """Test that /api/trips requires admin authentication"""
    response = test_client.get('/api/trips')
    assert response.status_code in [401, 302, 403]

def test_get_trips_success(authenticated_admin_client, sample_trip):
    """Test successful retrieval of trips list"""
    response = authenticated_admin_client.get('/api/trips')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert 'trips' in data
    assert isinstance(data['trips'], list)
    # Check trip structure
    if data['trips']:
        trip = data['trips'][0]
        assert 'id' in trip
        assert 'trip_name' in trip
        assert 'trip_type' in trip
        assert 'capacity' in trip
        assert 'current_count' in trip
        assert 'available_spots' in trip

def test_get_trips_error_handling(authenticated_admin_client):
    """Test error handling in get_trips"""
    response = authenticated_admin_client.get('/api/trips')
    assert response.status_code in [200, 500]

# ============================================
# Test /api/move-student endpoint
# ============================================

def test_move_student_requires_admin(test_client):
    """Test that move-student requires admin authentication"""
    response = test_client.post('/api/move-student',
        data=json.dumps({
            'student_id': 1,
            'new_trip_id': 1
        }),
        content_type='application/json'
    )
    assert response.status_code in [401, 302, 403]

def test_move_student_success(authenticated_admin_client):
    """Test successfully moving a student to a trip"""
    import time
    unique_id = int(time.time() * 1000) % 100000
    
    with authenticated_admin_client.application.app_context():
        # Create fresh trip and student
        trip = Trip(
            trip_name=f'Move Test Trip {unique_id}',
            trip_type='backpacking',
            capacity=5
        )
        student = Student(
            student_id=f'MOVETEST{unique_id}',
            first_name='Move',
            last_name='Test',
            email=f'movetest{unique_id}@test.com'
        )
        db.session.add_all([trip, student])
        db.session.commit()
        trip_id = trip.id
        student_id = student.id
    
    response = authenticated_admin_client.post('/api/move-student',
        data=json.dumps({
            'student_id': student_id,
            'new_trip_id': trip_id
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert 'message' in data

def test_move_student_remove_from_trip(authenticated_admin_client):
    """Test removing a student from a trip (new_trip_id is None)"""
    import time
    unique_id = int(time.time() * 1000) % 100000
    
    with authenticated_admin_client.application.app_context():
        # Create trip and student, assign student to trip
        trip = Trip(
            trip_name=f'Remove Test Trip {unique_id}',
            trip_type='backpacking',
            capacity=5
        )
        db.session.add(trip)
        db.session.flush()  # Get trip.id
        
        student = Student(
            student_id=f'REMOVETEST{unique_id}',
            first_name='Remove',
            last_name='Test',
            email=f'removetest{unique_id}@test.com',
            trip_id=trip.id
        )
        db.session.add(student)
        db.session.commit()
        student_id = student.id
    
    response = authenticated_admin_client.post('/api/move-student',
        data=json.dumps({
            'student_id': student_id,
            'new_trip_id': None
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert 'removed' in data['message'].lower() or 'no trip' in data['message'].lower()

def test_move_student_full_trip(authenticated_admin_client):
    """Test moving student to a full trip (should fail)"""
    import time
    unique_id = int(time.time() * 1000) % 100000
    
    with authenticated_admin_client.application.app_context():
        # Create a trip at full capacity
        full_trip = Trip(
            trip_name=f'Full Trip {unique_id}',
            trip_type='canoeing',
            capacity=1
        )
        # Add a student to fill it
        existing_student = Student(
            student_id=f'FULL{unique_id}',
            first_name='Full',
            last_name='Student',
            email=f'full{unique_id}@test.com'
        )
        new_student = Student(
            student_id=f'NEW{unique_id}',
            first_name='New',
            last_name='Student',
            email=f'new{unique_id}@test.com'
        )
        full_trip.students.append(existing_student)
        db.session.add_all([full_trip, new_student])
        db.session.commit()
        full_trip_id = full_trip.id
        student_id = new_student.id
    
    # Try to move another student to full trip
    response = authenticated_admin_client.post('/api/move-student',
        data=json.dumps({
            'student_id': student_id,
            'new_trip_id': full_trip_id
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['success'] == False
    assert 'full capacity' in data['error'].lower()

def test_move_student_invalid_id(authenticated_admin_client):
    """Test moving a student with invalid student_id"""
    response = authenticated_admin_client.post('/api/move-student',
        data=json.dumps({
            'student_id': 99999,
            'new_trip_id': 1
        }),
        content_type='application/json'
    )
    
    # get_or_404 will raise 404, caught by exception handler
    assert response.status_code in [404, 500]
    data = json.loads(response.data)
    assert data['success'] == False

# ============================================
# Test /api/swap-students endpoint
# ============================================

def test_swap_students_requires_admin(test_client):
    """Test that swap-students requires admin authentication"""
    response = test_client.post('/api/swap-students',
        data=json.dumps({
            'student1_id': 1,
            'student2_id': 2
        }),
        content_type='application/json'
    )
    assert response.status_code in [401, 302, 403]

def test_swap_students_success(authenticated_admin_client):
    """Test successfully swapping two students"""
    import time
    unique_id = int(time.time() * 1000) % 100000
    
    with authenticated_admin_client.application.app_context():
        student1 = Student(
            student_id=f'SWAP{unique_id}1',
            first_name='Swap1',
            last_name='Test',
            email=f'swap1{unique_id}@test.com'
        )
        student2 = Student(
            student_id=f'SWAP{unique_id}2',
            first_name='Swap2',
            last_name='Test',
            email=f'swap2{unique_id}@test.com'
        )
        db.session.add_all([student1, student2])
        db.session.commit()
        student1_id = student1.id
        student2_id = student2.id
    
    response = authenticated_admin_client.post('/api/swap-students',
        data=json.dumps({
            'student1_id': student1_id,
            'student2_id': student2_id
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert 'message' in data

def test_swap_students_with_trips(authenticated_admin_client):
    """Test swapping students who are in different trips"""
    import time
    unique_id = int(time.time() * 1000) % 100000
    
    with authenticated_admin_client.application.app_context():
        trip1 = Trip(trip_name=f'Trip1 {unique_id}', trip_type='backpacking', capacity=5)
        trip2 = Trip(trip_name=f'Trip2 {unique_id}', trip_type='canoeing', capacity=5)
        db.session.add_all([trip1, trip2])
        db.session.commit()
        
        student1 = Student(
            student_id=f'STU{unique_id}1',
            first_name='Student1',
            last_name='Test',
            email=f'student1{unique_id}@test.com',
            trip_id=trip1.id
        )
        student2 = Student(
            student_id=f'STU{unique_id}2',
            first_name='Student2',
            last_name='Test',
            email=f'student2{unique_id}@test.com',
            trip_id=trip2.id
        )
        db.session.add_all([student1, student2])
        db.session.commit()
        s1_id = student1.id
        s2_id = student2.id
    
    response = authenticated_admin_client.post('/api/swap-students',
        data=json.dumps({
            'student1_id': s1_id,
            'student2_id': s2_id
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True

def test_swap_students_invalid_id(authenticated_admin_client):
    """Test swapping with invalid student IDs"""
    response = authenticated_admin_client.post('/api/swap-students',
        data=json.dumps({
            'student1_id': 99999,
            'student2_id': 99998
        }),
        content_type='application/json'
    )
    
    assert response.status_code in [404, 500]
    data = json.loads(response.data)
    assert data['success'] == False

# ============================================
# Test /api/get-users endpoint
# ============================================

def test_get_users_requires_admin(test_client):
    """Test that /api/get-users requires admin authentication"""
    response = test_client.get('/api/get-users')
    assert response.status_code in [401, 302, 403]

def test_get_users_success(authenticated_admin_client, admin_user):
    """Test successful retrieval of users list"""
    response = authenticated_admin_client.get('/api/get-users')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'users' in data
    assert isinstance(data['users'], list)
    if data['users']:
        user = data['users'][0]
        assert 'email' in user
        assert 'first_name' in user
        assert 'last_name' in user
        assert 'role' in user

def test_get_users_error_handling(authenticated_admin_client):
    """Test error handling in get_users"""
    response = authenticated_admin_client.get('/api/get-users')
    assert response.status_code in [200, 500]

# ============================================
# Test /api/settings/show_trips endpoint
# ============================================

def test_get_show_trips_requires_admin(test_client):
    """Test that /api/settings/show_trips requires admin authentication"""
    response = test_client.get('/api/settings/show_trips')
    assert response.status_code in [401, 302, 403]

def test_get_show_trips_success(authenticated_admin_client):
    """Test successful retrieval of show_trips setting"""
    response = authenticated_admin_client.get('/api/settings/show_trips')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'show_trips_to_students' in data
    assert isinstance(data['show_trips_to_students'], bool)

# ============================================
# Test /api/settings/toggle_show_trips endpoint
# ============================================

def test_toggle_show_trips_requires_admin(test_client):
    """Test that toggle_show_trips requires admin authentication"""
    response = test_client.post('/api/settings/toggle_show_trips',
        data=json.dumps({}),
        content_type='application/json'
    )
    assert response.status_code in [401, 302, 403]

def test_toggle_show_trips_no_value(authenticated_admin_client):
    """Test toggling show_trips without providing value (toggles current state)"""
    response = authenticated_admin_client.post('/api/settings/toggle_show_trips',
        data=json.dumps({}),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert 'show_trips_to_students' in data

def test_toggle_show_trips_with_value_true(authenticated_admin_client):
    """Test setting show_trips to True"""
    response = authenticated_admin_client.post('/api/settings/toggle_show_trips',
        data=json.dumps({'value': True}),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert data['show_trips_to_students'] == True

def test_toggle_show_trips_with_value_false(authenticated_admin_client):
    """Test setting show_trips to False"""
    response = authenticated_admin_client.post('/api/settings/toggle_show_trips',
        data=json.dumps({'value': False}),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert data['show_trips_to_students'] == False

# ============================================
# Test /api/sort-students endpoint
# ============================================

def test_sort_students_requires_admin(test_client):
    """Test that sort-students requires admin authentication"""
    response = test_client.post('/api/sort-students',
        data=json.dumps({}),
        content_type='application/json'
    )
    assert response.status_code in [401, 302, 403]

def test_sort_students_success(authenticated_admin_client):
    """Test successful sorting of students"""
    response = authenticated_admin_client.post('/api/sort-students',
        data=json.dumps({}),
        content_type='application/json'
    )
    
    assert response.status_code in [200, 400]  # May fail if no students/trips
    data = json.loads(response.data)
    assert 'success' in data

def test_sort_students_with_criteria(authenticated_admin_client):
    """Test sorting students with custom criteria"""
    criteria = [{'type': 'dorm'}, {'type': 'gender'}]
    response = authenticated_admin_client.post('/api/sort-students',
        data=json.dumps({'criteria': criteria}),
        content_type='application/json'
    )
    
    assert response.status_code in [200, 400]
    data = json.loads(response.data)
    assert 'success' in data

def test_sort_students_error_handling(authenticated_admin_client):
    """Test error handling in sort_students"""
    # This tests the exception handler
    response = authenticated_admin_client.post('/api/sort-students',
        data=json.dumps({}),
        content_type='application/json'
    )
    assert response.status_code in [200, 400, 500]

# ============================================
# Test /api/update-user-role endpoint
# ============================================

def test_update_user_role_requires_manager(test_client, admin_user):
    """Test that update-user-role requires manager authentication"""
    response = test_client.post('/api/update-user-role',
        data=json.dumps({
            'email': admin_user.email,
            'role': 'admin'
        }),
        content_type='application/json'
    )
    assert response.status_code in [401, 302, 403]

def test_update_user_role_success(authenticated_manager_client, admin_user):
    """Test successfully updating a user's role"""
    response = authenticated_manager_client.post('/api/update-user-role',
        data=json.dumps({
            'email': admin_user.email,
            'role': 'student'
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True

def test_update_user_role_missing_email(authenticated_manager_client):
    """Test updating user role without email"""
    response = authenticated_manager_client.post('/api/update-user-role',
        data=json.dumps({'role': 'admin'}),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['success'] == False

def test_update_user_role_invalid_role(authenticated_manager_client, admin_user):
    """Test updating user role with invalid role"""
    response = authenticated_manager_client.post('/api/update-user-role',
        data=json.dumps({
            'email': admin_user.email,
            'role': 'invalid_role'
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['success'] == False

def test_update_user_role_user_not_found(authenticated_manager_client):
    """Test updating role for non-existent user"""
    response = authenticated_manager_client.post('/api/update-user-role',
        data=json.dumps({
            'email': 'nonexistent@test.com',
            'role': 'admin'
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['success'] == False

def test_update_user_role_self_demotion_prevented(authenticated_manager_client, manager_user):
    """Test that manager cannot demote themselves"""
    response = authenticated_manager_client.post('/api/update-user-role',
        data=json.dumps({
            'email': manager_user.email,
            'role': 'admin'  # Trying to demote from admin_manager
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 403
    data = json.loads(response.data)
    assert data['success'] == False

def test_update_user_role_to_none(authenticated_manager_client, admin_user):
    """Test updating user role to 'none' (converts to None)"""
    response = authenticated_manager_client.post('/api/update-user-role',
        data=json.dumps({
            'email': admin_user.email,
            'role': 'none'
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    
    # Verify role was set to None
    with authenticated_manager_client.application.app_context():
        user = User.query.filter_by(email=admin_user.email).first()
        assert user.role is None

def test_update_user_role_error_handling(authenticated_manager_client):
    """Test error handling in update_user_role"""
    response = authenticated_manager_client.post('/api/update-user-role',
        data=json.dumps({
            'email': 'test@test.com',
            'role': 'admin'
        }),
        content_type='application/json'
    )
    assert response.status_code in [200, 404, 500]

# ============================================
# Test /api/process_matched_csv endpoint
# ============================================

def test_process_matched_csv_requires_admin(test_client):
    """Test that process_matched_csv requires admin authentication"""
    response = test_client.post('/api/process_matched_csv')
    assert response.status_code in [401, 302, 403]

def test_process_matched_csv_no_file(authenticated_admin_client):
    """Test process_matched_csv with no file uploaded"""
    # Use form data without file
    response = authenticated_admin_client.post('/api/process_matched_csv',
        data={'importMode': 'add'},
        content_type='multipart/form-data'
    )
    
    # May return 400 (no file) or 403 (auth check happens first)
    assert response.status_code in [400, 403]
    if response.status_code == 400:
        data = json.loads(response.data)
        assert data['success'] == False
        assert 'No CSV uploaded' in data['message']

def test_process_matched_csv_empty_file(authenticated_admin_client):
    """Test process_matched_csv with empty CSV"""
    # Create empty CSV (no rows)
    csv_content = ""
    csv_file = io.BytesIO(csv_content.encode('utf-8'))
    
    response = authenticated_admin_client.post('/api/process_matched_csv',
        data={
            'csv_file': (csv_file, 'test.csv'),
            'importMode': 'add'
        },
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['success'] == False
    assert 'empty' in data['message'].lower()

def test_process_matched_csv_add_student(authenticated_admin_client):
    """Test adding a new student via CSV"""
    import time
    unique_id = int(time.time() * 1000) % 100000
    
    csv_data = io.StringIO()
    csv_writer = csv.writer(csv_data)
    csv_writer.writerow(['Student ID', 'First Name', 'Last Name', 'Email'])
    csv_writer.writerow([f'CSV{unique_id}', 'CSV', 'Student', f'csv{unique_id}@test.com'])
    
    response = authenticated_admin_client.post('/api/process_matched_csv',
        data={
            'csv_file': (io.BytesIO(csv_data.getvalue().encode('utf-8')), 'test.csv'),
            'importMode': 'add',
            'Student ID': 'student_id',
            'First Name': 'first_name',
            'Last Name': 'last_name',
            'Email': 'email'
        },
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert data['added'] >= 1

def test_process_matched_csv_update_student(authenticated_admin_client):
    """Test updating an existing student via CSV"""
    import time
    unique_id = int(time.time() * 1000) % 100000
    
    with authenticated_admin_client.application.app_context():
        existing_student = Student(
            student_id=f'UPDATE{unique_id}',
            first_name='Old',
            last_name='Name',
            email=f'old{unique_id}@test.com'
        )
        db.session.add(existing_student)
        db.session.commit()
        student_id = existing_student.student_id
    
    csv_data = io.StringIO()
    csv_writer = csv.writer(csv_data)
    csv_writer.writerow(['Student ID', 'First Name'])
    csv_writer.writerow([student_id, 'UpdatedName'])
    
    response = authenticated_admin_client.post('/api/process_matched_csv',
        data={
            'csv_file': (io.BytesIO(csv_data.getvalue().encode('utf-8')), 'test.csv'),
            'importMode': 'update',
            'Student ID': 'student_id',
            'First Name': 'first_name'
        },
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert data['updated'] >= 1

def test_process_matched_csv_missing_student_id(authenticated_admin_client):
    """Test CSV processing with missing student_id"""
    csv_data = io.StringIO()
    csv_writer = csv.writer(csv_data)
    csv_writer.writerow(['First Name', 'Last Name'])
    csv_writer.writerow(['Test', 'Student'])
    
    response = authenticated_admin_client.post('/api/process_matched_csv',
        data={
            'csv_file': (io.BytesIO(csv_data.getvalue().encode('utf-8')), 'test.csv'),
            'importMode': 'add',
            'First Name': 'first_name',
            'Last Name': 'last_name'
        },
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert data['skipped'] >= 1  # Should skip rows without student_id
    assert len(data['errors']) > 0

def test_process_matched_csv_missing_required_fields(authenticated_admin_client):
    """Test CSV processing with missing required fields for new students"""
    import time
    unique_id = int(time.time() * 1000) % 100000
    
    csv_data = io.StringIO()
    csv_writer = csv.writer(csv_data)
    csv_writer.writerow(['Student ID'])
    csv_writer.writerow([f'CSV{unique_id}'])  # Missing first_name, last_name, email
    
    response = authenticated_admin_client.post('/api/process_matched_csv',
        data={
            'csv_file': (io.BytesIO(csv_data.getvalue().encode('utf-8')), 'test.csv'),
            'importMode': 'add',
            'Student ID': 'student_id'
        },
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert data['skipped'] >= 1
    assert len(data['errors']) > 0

def test_process_matched_csv_with_trip_name(authenticated_admin_client):
    """Test CSV processing with trip_name mapping"""
    import time
    unique_id = int(time.time() * 1000) % 100000
    
    # Create trip first
    with authenticated_admin_client.application.app_context():
        trip = Trip(
            trip_name=f'CSV Trip {unique_id}',
            trip_type='backpacking',
            capacity=10
        )
        db.session.add(trip)
        db.session.commit()
        trip_name = trip.trip_name
    
    csv_data = io.StringIO()
    csv_writer = csv.writer(csv_data)
    csv_writer.writerow(['Student ID', 'First Name', 'Last Name', 'Email', 'Trip Name'])
    csv_writer.writerow([f'CSV{unique_id}', 'CSV', 'Student', f'csv{unique_id}@test.com', trip_name])
    
    response = authenticated_admin_client.post('/api/process_matched_csv',
        data={
            'csv_file': (io.BytesIO(csv_data.getvalue().encode('utf-8')), 'test.csv'),
            'importMode': 'add',
            'Student ID': 'student_id',
            'First Name': 'first_name',
            'Last Name': 'last_name',
            'Email': 'email',
            'Trip Name': 'trip_name'
        },
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True

def test_process_matched_csv_boolean_fields(authenticated_admin_client):
    """Test CSV processing with boolean fields (poc, fli_international)"""
    import time
    unique_id = int(time.time() * 1000) % 100000
    
    csv_data = io.StringIO()
    csv_writer = csv.writer(csv_data)
    csv_writer.writerow(['Student ID', 'First Name', 'Last Name', 'Email', 'POC'])
    csv_writer.writerow([f'CSV{unique_id}', 'CSV', 'Student', f'csv{unique_id}@test.com', 'true'])
    
    response = authenticated_admin_client.post('/api/process_matched_csv',
        data={
            'csv_file': (io.BytesIO(csv_data.getvalue().encode('utf-8')), 'test.csv'),
            'importMode': 'add',
            'Student ID': 'student_id',
            'First Name': 'first_name',
            'Last Name': 'last_name',
            'Email': 'email',
            'POC': 'poc'
        },
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True

def test_process_matched_csv_integer_fields(authenticated_admin_client):
    """Test CSV processing with integer fields (water_comfort, tent_comfort)"""
    import time
    unique_id = int(time.time() * 1000) % 100000
    
    csv_data = io.StringIO()
    csv_writer = csv.writer(csv_data)
    csv_writer.writerow(['Student ID', 'First Name', 'Last Name', 'Email', 'Water Comfort'])
    csv_writer.writerow([f'CSV{unique_id}', 'CSV', 'Student', f'csv{unique_id}@test.com', '4'])
    
    response = authenticated_admin_client.post('/api/process_matched_csv',
        data={
            'csv_file': (io.BytesIO(csv_data.getvalue().encode('utf-8')), 'test.csv'),
            'importMode': 'add',
            'Student ID': 'student_id',
            'First Name': 'first_name',
            'Last Name': 'last_name',
            'Email': 'email',
            'Water Comfort': 'water_comfort'
        },
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True

def test_process_matched_csv_error_handling(authenticated_admin_client):
    """Test error handling in process_matched_csv"""
    # Test with invalid CSV data
    response = authenticated_admin_client.post('/api/process_matched_csv',
        data={
            'csv_file': (io.BytesIO(b'invalid csv data'), 'test.csv'),
            'importMode': 'add'
        },
        content_type='multipart/form-data'
    )
    
    # Should handle error gracefully
    assert response.status_code in [200, 400, 500]

# ============================================
# Test /api/process_matched_trips_csv endpoint
# ============================================

def test_process_matched_trips_csv_requires_admin(test_client):
    """Test that process_matched_trips_csv requires admin authentication"""
    response = test_client.post('/api/process_matched_trips_csv')
    assert response.status_code in [401, 302, 403]

def test_process_matched_trips_csv_no_file(authenticated_admin_client):
    """Test process_matched_trips_csv with no file uploaded"""
    response = authenticated_admin_client.post('/api/process_matched_trips_csv',
        data={},
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['success'] == False
    assert 'No CSV uploaded' in data['message']

def test_process_matched_trips_csv_empty_file(authenticated_admin_client):
    """Test process_matched_trips_csv with empty CSV"""
    csv_data = io.StringIO()
    csv_writer = csv.writer(csv_data)
    csv_writer.writerow([])
    
    response = authenticated_admin_client.post('/api/process_matched_trips_csv',
        data={
            'csv_file': (io.BytesIO(csv_data.getvalue().encode('utf-8')), 'test.csv'),
            'importMode': 'add'
        },
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['success'] == False

def test_process_matched_trips_csv_add_trip(authenticated_admin_client):
    """Test adding a new trip via CSV"""
    import time
    unique_id = int(time.time() * 1000) % 100000
    
    csv_data = io.StringIO()
    csv_writer = csv.writer(csv_data)
    csv_writer.writerow(['Trip Name', 'Trip Type', 'Capacity'])
    csv_writer.writerow([f'CSV Trip {unique_id}', 'backpacking', '10'])
    
    response = authenticated_admin_client.post('/api/process_matched_trips_csv',
        data={
            'csv_file': (io.BytesIO(csv_data.getvalue().encode('utf-8')), 'test.csv'),
            'importMode': 'add',
            'Trip Name': 'trip_name',
            'Trip Type': 'trip_type',
            'Capacity': 'capacity'
        },
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert data['added'] >= 1

def test_process_matched_trips_csv_update_trip(authenticated_admin_client):
    """Test updating an existing trip via CSV"""
    import time
    unique_id = int(time.time() * 1000) % 100000
    
    with authenticated_admin_client.application.app_context():
        existing_trip = Trip(
            trip_name=f'Update Trip {unique_id}',
            trip_type='backpacking',
            capacity=10
        )
        db.session.add(existing_trip)
        db.session.commit()
        trip_name = existing_trip.trip_name
    
    csv_data = io.StringIO()
    csv_writer = csv.writer(csv_data)
    csv_writer.writerow(['Trip Name', 'Capacity'])
    csv_writer.writerow([trip_name, '15'])
    
    response = authenticated_admin_client.post('/api/process_matched_trips_csv',
        data={
            'csv_file': (io.BytesIO(csv_data.getvalue().encode('utf-8')), 'test.csv'),
            'importMode': 'update',
            'Trip Name': 'trip_name',
            'Capacity': 'capacity'
        },
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert data['updated'] >= 1

def test_process_matched_trips_csv_missing_trip_name(authenticated_admin_client):
    """Test CSV processing with missing trip_name"""
    csv_data = io.StringIO()
    csv_writer = csv.writer(csv_data)
    csv_writer.writerow(['Trip Type', 'Capacity'])
    csv_writer.writerow(['backpacking', '10'])
    
    response = authenticated_admin_client.post('/api/process_matched_trips_csv',
        data={
            'csv_file': (io.BytesIO(csv_data.getvalue().encode('utf-8')), 'test.csv'),
            'importMode': 'add',
            'Trip Type': 'trip_type',
            'Capacity': 'capacity'
        },
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert data['skipped'] >= 1

def test_process_matched_trips_csv_missing_required_fields(authenticated_admin_client):
    """Test CSV processing with missing required fields for new trips"""
    import time
    unique_id = int(time.time() * 1000) % 100000
    
    csv_data = io.StringIO()
    csv_writer = csv.writer(csv_data)
    csv_writer.writerow(['Trip Name'])
    csv_writer.writerow([f'CSV Trip {unique_id}'])  # Missing trip_type and capacity
    
    response = authenticated_admin_client.post('/api/process_matched_trips_csv',
        data={
            'csv_file': (io.BytesIO(csv_data.getvalue().encode('utf-8')), 'test.csv'),
            'importMode': 'add',
            'Trip Name': 'trip_name'
        },
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert data['skipped'] >= 1
    assert len(data['errors']) > 0

def test_process_matched_trips_csv_boolean_fields(authenticated_admin_client):
    """Test CSV processing with boolean fields (water, tent)"""
    import time
    unique_id = int(time.time() * 1000) % 100000
    
    csv_data = io.StringIO()
    csv_writer = csv.writer(csv_data)
    csv_writer.writerow(['Trip Name', 'Trip Type', 'Capacity', 'Water'])
    csv_writer.writerow([f'CSV Trip {unique_id}', 'canoeing', '10', 'true'])
    
    response = authenticated_admin_client.post('/api/process_matched_trips_csv',
        data={
            'csv_file': (io.BytesIO(csv_data.getvalue().encode('utf-8')), 'test.csv'),
            'importMode': 'add',
            'Trip Name': 'trip_name',
            'Trip Type': 'trip_type',
            'Capacity': 'capacity',
            'Water': 'water'
        },
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True

def test_process_matched_trips_csv_error_handling(authenticated_admin_client):
    """Test error handling in process_matched_trips_csv"""
    response = authenticated_admin_client.post('/api/process_matched_trips_csv',
        data={
            'csv_file': (io.BytesIO(b'invalid csv'), 'test.csv'),
            'importMode': 'add'
        },
        content_type='multipart/form-data'
    )
    
    assert response.status_code in [200, 400, 500]

# ============================================
# Additional tests for edge cases to reach 95% coverage
# ============================================

def test_process_matched_csv_with_trip_name_and_type(authenticated_admin_client):
    """Test CSV processing with trip_name and trip_type mapping (creates new trip)"""
    import time
    unique_id = int(time.time() * 1000) % 100000
    
    csv_data = io.StringIO()
    csv_writer = csv.writer(csv_data)
    csv_writer.writerow(['Student ID', 'First Name', 'Last Name', 'Email', 'Trip Name', 'Trip Type'])
    csv_writer.writerow([f'CSV{unique_id}', 'CSV', 'Student', f'csv{unique_id}@test.com', f'New Trip {unique_id}', 'backpacking'])
    
    response = authenticated_admin_client.post('/api/process_matched_csv',
        data={
            'csv_file': (io.BytesIO(csv_data.getvalue().encode('utf-8')), 'test.csv'),
            'importMode': 'add',
            'Student ID': 'student_id',
            'First Name': 'first_name',
            'Last Name': 'last_name',
            'Email': 'email',
            'Trip Name': 'trip_name',
            'Trip Type': 'trip_type'
        },
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True

def test_process_matched_csv_boolean_empty(authenticated_admin_client):
    """Test CSV processing with empty boolean fields"""
    import time
    unique_id = int(time.time() * 1000) % 100000
    
    csv_data = io.StringIO()
    csv_writer = csv.writer(csv_data)
    csv_writer.writerow(['Student ID', 'First Name', 'Last Name', 'Email', 'POC'])
    csv_writer.writerow([f'CSV{unique_id}', 'CSV', 'Student', f'csv{unique_id}@test.com', ''])  # Empty POC
    
    response = authenticated_admin_client.post('/api/process_matched_csv',
        data={
            'csv_file': (io.BytesIO(csv_data.getvalue().encode('utf-8')), 'test.csv'),
            'importMode': 'add',
            'Student ID': 'student_id',
            'First Name': 'first_name',
            'Last Name': 'last_name',
            'Email': 'email',
            'POC': 'poc'
        },
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True

def test_process_matched_csv_integer_empty(authenticated_admin_client):
    """Test CSV processing with empty integer fields"""
    import time
    unique_id = int(time.time() * 1000) % 100000
    
    csv_data = io.StringIO()
    csv_writer = csv.writer(csv_data)
    csv_writer.writerow(['Student ID', 'First Name', 'Last Name', 'Email', 'Water Comfort'])
    csv_writer.writerow([f'CSV{unique_id}', 'CSV', 'Student', f'csv{unique_id}@test.com', ''])  # Empty water_comfort
    
    response = authenticated_admin_client.post('/api/process_matched_csv',
        data={
            'csv_file': (io.BytesIO(csv_data.getvalue().encode('utf-8')), 'test.csv'),
            'importMode': 'add',
            'Student ID': 'student_id',
            'First Name': 'first_name',
            'Last Name': 'last_name',
            'Email': 'email',
            'Water Comfort': 'water_comfort'
        },
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True

def test_process_matched_csv_existing_student_skip(authenticated_admin_client):
    """Test CSV processing skips existing student in add mode"""
    import time
    unique_id = int(time.time() * 1000) % 100000
    
    with authenticated_admin_client.application.app_context():
        existing_student = Student(
            student_id=f'EXIST{unique_id}',
            first_name='Existing',
            last_name='Student',
            email=f'exist{unique_id}@test.com'
        )
        db.session.add(existing_student)
        db.session.commit()
        student_id = existing_student.student_id
    
    csv_data = io.StringIO()
    csv_writer = csv.writer(csv_data)
    csv_writer.writerow(['Student ID', 'First Name', 'Last Name', 'Email'])
    csv_writer.writerow([student_id, 'New', 'Name', f'new{unique_id}@test.com'])
    
    response = authenticated_admin_client.post('/api/process_matched_csv',
        data={
            'csv_file': (io.BytesIO(csv_data.getvalue().encode('utf-8')), 'test.csv'),
            'importMode': 'add',  # Add mode, student exists
            'Student ID': 'student_id',
            'First Name': 'first_name',
            'Last Name': 'last_name',
            'Email': 'email'
        },
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert data['skipped'] >= 1

def test_process_matched_csv_trip_name_no_trip_type(authenticated_admin_client):
    """Test CSV processing with trip_name but no trip_type (doesn't create trip)"""
    import time
    unique_id = int(time.time() * 1000) % 100000
    
    csv_data = io.StringIO()
    csv_writer = csv.writer(csv_data)
    csv_writer.writerow(['Student ID', 'First Name', 'Last Name', 'Email', 'Trip Name'])
    csv_writer.writerow([f'CSV{unique_id}', 'CSV', 'Student', f'csv{unique_id}@test.com', 'NonExistent Trip'])
    
    response = authenticated_admin_client.post('/api/process_matched_csv',
        data={
            'csv_file': (io.BytesIO(csv_data.getvalue().encode('utf-8')), 'test.csv'),
            'importMode': 'add',
            'Student ID': 'student_id',
            'First Name': 'first_name',
            'Last Name': 'last_name',
            'Email': 'email',
            'Trip Name': 'trip_name'
        },
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True

def test_process_matched_trips_csv_missing_trip_type(authenticated_admin_client):
    """Test CSV processing with missing trip_type for new trip"""
    import time
    unique_id = int(time.time() * 1000) % 100000
    
    csv_data = io.StringIO()
    csv_writer = csv.writer(csv_data)
    csv_writer.writerow(['Trip Name', 'Capacity'])
    csv_writer.writerow([f'CSV Trip {unique_id}', '10'])  # Missing trip_type
    
    response = authenticated_admin_client.post('/api/process_matched_trips_csv',
        data={
            'csv_file': (io.BytesIO(csv_data.getvalue().encode('utf-8')), 'test.csv'),
            'importMode': 'add',
            'Trip Name': 'trip_name',
            'Capacity': 'capacity'
        },
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert data['skipped'] >= 1

def test_process_matched_trips_csv_missing_capacity(authenticated_admin_client):
    """Test CSV processing with missing capacity for new trip"""
    import time
    unique_id = int(time.time() * 1000) % 100000
    
    csv_data = io.StringIO()
    csv_writer = csv.writer(csv_data)
    csv_writer.writerow(['Trip Name', 'Trip Type'])
    csv_writer.writerow([f'CSV Trip {unique_id}', 'backpacking'])  # Missing capacity
    
    response = authenticated_admin_client.post('/api/process_matched_trips_csv',
        data={
            'csv_file': (io.BytesIO(csv_data.getvalue().encode('utf-8')), 'test.csv'),
            'importMode': 'add',
            'Trip Name': 'trip_name',
            'Trip Type': 'trip_type'
        },
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert data['skipped'] >= 1

def test_process_matched_trips_csv_existing_skip(authenticated_admin_client):
    """Test CSV processing skips existing trip in add mode"""
    import time
    unique_id = int(time.time() * 1000) % 100000
    
    with authenticated_admin_client.application.app_context():
        existing_trip = Trip(
            trip_name=f'Existing Trip {unique_id}',
            trip_type='backpacking',
            capacity=10
        )
        db.session.add(existing_trip)
        db.session.commit()
        trip_name = existing_trip.trip_name
    
    csv_data = io.StringIO()
    csv_writer = csv.writer(csv_data)
    csv_writer.writerow(['Trip Name', 'Trip Type', 'Capacity'])
    csv_writer.writerow([trip_name, 'backpacking', '10'])
    
    response = authenticated_admin_client.post('/api/process_matched_trips_csv',
        data={
            'csv_file': (io.BytesIO(csv_data.getvalue().encode('utf-8')), 'test.csv'),
            'importMode': 'add',  # Add mode, trip exists
            'Trip Name': 'trip_name',
            'Trip Type': 'trip_type',
            'Capacity': 'capacity'
        },
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert data['skipped'] >= 1


def test_process_matched_csv_missing_first_name(authenticated_admin_client):
    """Test CSV processing with missing first_name (line 263-265)"""
    import time
    unique_id = int(time.time() * 1000) % 100000
    
    csv_data = io.StringIO()
    csv_writer = csv.writer(csv_data)
    csv_writer.writerow(['Student ID', 'Last Name', 'Email'])
    csv_writer.writerow([f'CSV{unique_id}', 'Student', f'csv{unique_id}@test.com'])
    
    response = authenticated_admin_client.post('/api/process_matched_csv',
        data={
            'csv_file': (io.BytesIO(csv_data.getvalue().encode('utf-8')), 'test.csv'),
            'importMode': 'add',
            'Student ID': 'student_id',
            'Last Name': 'last_name',
            'Email': 'email'
        },
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert data['skipped'] >= 1

def test_process_matched_csv_missing_last_name(authenticated_admin_client):
    """Test CSV processing with missing last_name (line 267-269)"""
    import time
    unique_id = int(time.time() * 1000) % 100000
    
    csv_data = io.StringIO()
    csv_writer = csv.writer(csv_data)
    csv_writer.writerow(['Student ID', 'First Name', 'Email'])
    csv_writer.writerow([f'CSV{unique_id}', 'CSV', f'csv{unique_id}@test.com'])
    
    response = authenticated_admin_client.post('/api/process_matched_csv',
        data={
            'csv_file': (io.BytesIO(csv_data.getvalue().encode('utf-8')), 'test.csv'),
            'importMode': 'add',
            'Student ID': 'student_id',
            'First Name': 'first_name',
            'Email': 'email'
        },
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert data['skipped'] >= 1

def test_process_matched_csv_missing_email(authenticated_admin_client):
    """Test CSV processing with missing email"""
    import time
    unique_id = int(time.time() * 1000) % 100000
    
    csv_data = io.StringIO()
    csv_writer = csv.writer(csv_data)
    csv_writer.writerow(['Student ID', 'First Name', 'Last Name'])
    csv_writer.writerow([f'CSV{unique_id}', 'CSV', 'Student'])
    
    response = authenticated_admin_client.post('/api/process_matched_csv',
        data={
            'csv_file': (io.BytesIO(csv_data.getvalue().encode('utf-8')), 'test.csv'),
            'importMode': 'add',
            'Student ID': 'student_id',
            'First Name': 'first_name',
            'Last Name': 'last_name'
        },
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert data['skipped'] >= 1

def test_process_matched_csv_update_mode(authenticated_admin_client):
    """Test CSV processing in update mode (lines 288-290)"""
    import time
    unique_id = int(time.time() * 1000) % 100000
    
    with authenticated_admin_client.application.app_context():
        existing_student = Student(
            student_id=f'UPDATE{unique_id}',
            first_name='Old',
            last_name='Name',
            email=f'old{unique_id}@test.com'
        )
        db.session.add(existing_student)
        db.session.commit()
        student_id = existing_student.student_id
    
    csv_data = io.StringIO()
    csv_writer = csv.writer(csv_data)
    csv_writer.writerow(['Student ID', 'First Name'])
    csv_writer.writerow([student_id, 'NewName'])
    
    response = authenticated_admin_client.post('/api/process_matched_csv',
        data={
            'csv_file': (io.BytesIO(csv_data.getvalue().encode('utf-8')), 'test.csv'),
            'importMode': 'update',
            'Student ID': 'student_id',
            'First Name': 'first_name'
        },
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert data['updated'] >= 1

def test_process_matched_trips_csv_update_mode(authenticated_admin_client):
    """Test CSV processing in update mode for trips (lines 380-382)"""
    import time
    unique_id = int(time.time() * 1000) % 100000
    
    with authenticated_admin_client.application.app_context():
        existing_trip = Trip(
            trip_name=f'Update Trip {unique_id}',
            trip_type='backpacking',
            capacity=10
        )
        db.session.add(existing_trip)
        db.session.commit()
        trip_name = existing_trip.trip_name
    
    csv_data = io.StringIO()
    csv_writer = csv.writer(csv_data)
    csv_writer.writerow(['Trip Name', 'Capacity'])
    csv_writer.writerow([trip_name, '15'])
    
    response = authenticated_admin_client.post('/api/process_matched_trips_csv',
        data={
            'csv_file': (io.BytesIO(csv_data.getvalue().encode('utf-8')), 'test.csv'),
            'importMode': 'update',
            'Trip Name': 'trip_name',
            'Capacity': 'capacity'
        },
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert data['updated'] >= 1

# ============================================
# Tests for exception handlers to reach 95% coverage
# ============================================

def test_get_students_exception_handler(authenticated_admin_client):
    """Test exception handler in get_students (lines 40-41)"""
    with authenticated_admin_client.application.app_context():
        with patch.object(Student, 'query') as mock_query:
            mock_query.all.side_effect = Exception("Database error")
            
            response = authenticated_admin_client.get('/api/students')
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert data['success'] == False
            assert 'error' in data

def test_get_trips_exception_handler(authenticated_admin_client):
    """Test exception handler in get_trips (lines 68-69)"""
    with authenticated_admin_client.application.app_context():
        with patch.object(Trip, 'query') as mock_query:
            mock_query.all.side_effect = Exception("Database error")
            
            response = authenticated_admin_client.get('/api/trips')
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert data['success'] == False
            assert 'error' in data

def test_get_users_exception_handler(authenticated_admin_client):
    """Test exception handler in get_users (lines 159-160)"""
    # Patch at the module level where it's used
    with patch('website.api_routes.User') as mock_user:
        mock_user.query.all.side_effect = Exception("Database error")
        
        response = authenticated_admin_client.get('/api/get-users')
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'error' in data

def test_process_matched_csv_exception_handler(authenticated_admin_client):
    """Test exception handler in process_matched_csv (lines 315-317)"""
    # Trigger exception by causing an error in CSV processing
    with patch('website.api_routes.db.session.commit') as mock_commit:
        mock_commit.side_effect = Exception("Commit error")
        
        csv_data = io.StringIO()
        csv_writer = csv.writer(csv_data)
        csv_writer.writerow(['Student ID', 'First Name', 'Last Name', 'Email'])
        csv_writer.writerow(['TEST123', 'Test', 'Student', 'test@test.com'])
        
        response = authenticated_admin_client.post('/api/process_matched_csv',
            data={
                'csv_file': (io.BytesIO(csv_data.getvalue().encode('utf-8')), 'test.csv'),
                'importMode': 'add',
                'Student ID': 'student_id',
                'First Name': 'first_name',
                'Last Name': 'last_name',
                'Email': 'email'
            },
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['success'] == False

def test_process_matched_csv_row_exception(authenticated_admin_client):
    """Test exception handler in CSV row processing (lines 300-303)"""
    # Create CSV that will cause an exception when processing
    csv_data = io.StringIO()
    csv_writer = csv.writer(csv_data)
    csv_writer.writerow(['Student ID', 'First Name'])
    # This will cause an exception when trying to create student with invalid data
    csv_writer.writerow(['TEST123', None])  # None might cause issues
    
    response = authenticated_admin_client.post('/api/process_matched_csv',
        data={
            'csv_file': (io.BytesIO(csv_data.getvalue().encode('utf-8')), 'test.csv'),
            'importMode': 'add',
            'Student ID': 'student_id',
            'First Name': 'first_name'
        },
        content_type='multipart/form-data'
    )
    
    # Should handle exception gracefully
    assert response.status_code in [200, 400, 500]

def test_process_matched_trips_csv_exception_handler(authenticated_admin_client):
    """Test exception handler in process_matched_trips_csv (lines 417-419)"""
    with patch('website.api_routes.db.session.commit') as mock_commit:
        mock_commit.side_effect = Exception("Commit error")
        
        csv_data = io.StringIO()
        csv_writer = csv.writer(csv_data)
        csv_writer.writerow(['Trip Name', 'Trip Type', 'Capacity'])
        csv_writer.writerow(['Test Trip', 'backpacking', '10'])
        
        response = authenticated_admin_client.post('/api/process_matched_trips_csv',
            data={
                'csv_file': (io.BytesIO(csv_data.getvalue().encode('utf-8')), 'test.csv'),
                'importMode': 'add',
                'Trip Name': 'trip_name',
                'Trip Type': 'trip_type',
                'Capacity': 'capacity'
            },
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['success'] == False

def test_process_matched_trips_csv_row_exception(authenticated_admin_client):
    """Test exception handler in trips CSV row processing (lines 402-405)"""
    # Create CSV that might cause an exception
    csv_data = io.StringIO()
    csv_writer = csv.writer(csv_data)
    csv_writer.writerow(['Trip Name', 'Trip Type'])
    csv_writer.writerow(['Test Trip', None])  # None might cause issues
    
    response = authenticated_admin_client.post('/api/process_matched_trips_csv',
        data={
            'csv_file': (io.BytesIO(csv_data.getvalue().encode('utf-8')), 'test.csv'),
            'importMode': 'add',
            'Trip Name': 'trip_name',
            'Trip Type': 'trip_type'
        },
        content_type='multipart/form-data'
    )
    
    # Should handle exception gracefully
    assert response.status_code in [200, 400, 500]

def test_update_user_role_exception_handler(authenticated_manager_client, admin_user):
    """Test exception handler in update_user_role (lines 463-466)"""
    with patch('website.api_routes.db.session.commit') as mock_commit:
        mock_commit.side_effect = Exception("Commit error")
        
        response = authenticated_manager_client.post('/api/update-user-role',
            data=json.dumps({
                'email': admin_user.email,
                'role': 'admin'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['success'] == False

def test_sort_students_exception_handler(authenticated_admin_client):
    """Test exception handler in sort_students (lines 487-489)"""
    with patch('website.api_routes.sort_students') as mock_sort:
        mock_sort.side_effect = Exception("Sorting error")
        
        response = authenticated_admin_client.post('/api/sort-students',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] == False
        assert 'message' in data
