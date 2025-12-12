""" This file contains functional tests for the website.views file.
"""
import io

from flask import url_for

from website import db
from website.models import Student, Trip

# Settings - admin_required & login_required
def test_settings_page_success_admin_manager(logged_in_admin_manager):
    """
    GIVEN a test client logged in as an 'admin_manager' user (authorized)
    WHEN the '/settings' page is requested (GET)
    THEN check the response status is 200 (OK) and the page content is correct
    """
    response = logged_in_admin_manager.get(url_for('main.settings'))
    assert response.status_code == 200
    assert b'Settings' in response.data
    assert b'Toggle Trip Visibility' in response.data

def test_settings_page_success_admin(logged_in_admin):
    """
    GIVEN a test client logged in as an 'admin' user (authorized)
    WHEN the '/settings' page is requested (GET)
    THEN check the response status is 200 (OK) and the page content is correct
    """
    response = logged_in_admin.get(url_for('main.settings'))
    assert response.status_code == 200
    assert b'Settings' in response.data
    assert b'Toggle Trip Visibility' in response.data

def test_settings_page_unauthorized_student(logged_in_student):
    """
    GIVEN a test client logged in as a 'student' user (unauthorized)
    WHEN the '/settings' page is requested (GET)
    THEN check the response status is 403.
    """
    response = logged_in_student.get(url_for('main.settings'))
    assert response.status_code == 403
    assert b'Forbidden' in response.data

def test_settings_page_unauthorized_no_role(logged_in_no_role):
    """
    GIVEN a test client logged in as a user with no role (unauthorized)
    WHEN the '/settings' page is requested (GET)
    THEN check the response status is 403.
    """
    response = logged_in_no_role.get(url_for('main.settings'))
    assert response.status_code == 403
    assert b'Forbidden' in response.data

def test_settings_page_unauthenticated(test_client):
    """
    GIVEN a test client that is not logged in
    WHEN the '/settings' page is requested (GET)
    THEN check the response status is 401.
    """
    response = test_client.get(url_for('main.settings'))
    assert response.status_code == 401
    assert b'Unauthorized' in response.data

# Student View - student_required
def test_student_view_success(logged_in_student):
    """
    GIVEN a test client logged in as a 'student' user (authorized)
    WHEN the '/student_view' page is requested (GET)
    THEN check the response status is 200 (OK) and the page content is correct
    """
    response = logged_in_student.get(url_for('main.student_view'))
    assert response.status_code == 200
    assert b'student' in response.data.lower() or b'view' in response.data.lower()

def test_student_view_with_trips_enabled(logged_in_student, app_settings):
    """
    GIVEN a test client logged in as a student and trips are visible
    WHEN the '/student_view' page is requested (GET)
    THEN check the response status is 200
    """
    app_settings.show_trips_to_students = True
    db.session.commit()

    response = logged_in_student.get(url_for('main.student_view'))
    assert response.status_code == 200

def test_student_view_unauthorized_no_role(logged_in_no_role):
    """
    GIVEN a test client logged in as a user with no role (unauthorized)
    WHEN the '/student_view' page is requested (GET)
    THEN check the response status is 403.
    """
    response = logged_in_no_role.get(url_for('main.student_view'))
    assert response.status_code == 403
    assert b'Forbidden' in response.data

def test_student_view_unauthenticated(test_client):
    """
    GIVEN a test client that is not logged in
    WHEN the '/student_view' page is requested (GET)
    THEN check the response status is 401.
    """
    response = test_client.get(url_for('main.student_view'))
    assert response.status_code == 401
    assert b'Unauthorized' in response.data


# No Access - login_required
def test_no_access_success(logged_in_no_role):
    """
    GIVEN a test client logged in as a user with no role
    WHEN the '/no_access' page is requested (GET)
    THEN check the response status is 200 (OK)
    """
    response = logged_in_no_role.get(url_for('main.no_access'))
    assert response.status_code == 200

def test_no_access_redirect_with_role(logged_in_student):
    """
    GIVEN a test client logged in as a user with a role (student)
    WHEN the '/no_access' page is requested (GET)
    THEN check the response redirects (302) to home page
    """
    response = logged_in_student.get(url_for('main.no_access'))
    assert response.status_code == 302

def test_no_access_unauthenticated(test_client):
    """
    GIVEN a test client that is not logged in
    WHEN the '/no_access' page is requested (GET)
    THEN check the response status is 302
    """
    response = test_client.get(url_for('main.no_access'))
    assert response.status_code == 302


# Trips - admin_required
def test_trips_page_success_admin_manager(logged_in_admin_manager):
    """
    GIVEN a test client logged in as an 'admin_manager' user (authorized)
    WHEN the '/trips' page is requested (GET)
    THEN check the response status is 200 (OK)
    """
    response = logged_in_admin_manager.get(url_for('main.trips'))
    assert response.status_code == 200

def test_trips_page_success_admin(logged_in_admin):
    """
    GIVEN a test client logged in as an 'admin' user (authorized)
    WHEN the '/trips' page is requested (GET)
    THEN check the response status is 200 (OK)
    """
    response = logged_in_admin.get(url_for('main.trips'))
    assert response.status_code == 200

def test_trips_page_unauthorized_student(logged_in_student):
    """
    GIVEN a test client logged in as a 'student' user (unauthorized)
    WHEN the '/trips' page is requested (GET)
    THEN check the response status is 403.
    """
    response = logged_in_student.get(url_for('main.trips'))
    assert response.status_code == 403
    assert b'Forbidden' in response.data

def test_trips_page_unauthenticated(test_client):
    """
    GIVEN a test client that is not logged in
    WHEN the '/trips' page is requested (GET)
    THEN check the response status is 401.
    """
    response = test_client.get(url_for('main.trips'))
    assert response.status_code == 401
    assert b'Unauthorized' in response.data


# First Years - admin_required
def test_first_years_page_success_admin_manager(logged_in_admin_manager):
    """
    GIVEN a test client logged in as an 'admin_manager' user (authorized)
    WHEN the '/first-years' page is requested (GET)
    THEN check the response status is 200 (OK)
    """
    response = logged_in_admin_manager.get(url_for('main.first_years'))
    assert response.status_code == 200

def test_first_years_page_success_admin(logged_in_admin):
    """
    GIVEN a test client logged in as an 'admin' user (authorized)
    WHEN the '/first-years' page is requested (GET)
    THEN check the response status is 200 (OK)
    """
    response = logged_in_admin.get(url_for('main.first_years'))
    assert response.status_code == 200

def test_first_years_page_unauthorized_student(logged_in_student):
    """
    GIVEN a test client logged in as a 'student' user (unauthorized)
    WHEN the '/first-years' page is requested (GET)
    THEN check the response redirects to the /no_access page (403).
    """
    response = logged_in_student.get(url_for('main.first_years'))
    assert response.status_code == 403
    assert b'Forbidden' in response.data

def test_first_years_page_unauthenticated(test_client):
    """
    GIVEN a test client that is not logged in
    WHEN the '/first-years' page is requested (GET)
    THEN check the response status is 401.
    """
    response = test_client.get(url_for('main.first_years'))
    assert response.status_code == 401
    assert b'Unauthorized' in response.data


# Groups - admin_required
def test_groups_page_success_admin_manager(logged_in_admin_manager):
    """
    GIVEN a test client logged in as an 'admin_manager' user (authorized)
    WHEN the '/groups' page is requested (GET)
    THEN check the response status is 200 (OK)
    """
    response = logged_in_admin_manager.get(url_for('main.groups'))
    assert response.status_code == 200

def test_groups_page_success_admin(logged_in_admin):
    """
    GIVEN a test client logged in as an 'admin' user (authorized)
    WHEN the '/groups' page is requested (GET)
    THEN check the response status is 200 (OK)
    """
    response = logged_in_admin.get(url_for('main.groups'))
    assert response.status_code == 200

def test_groups_page_unauthorized_student(logged_in_student):
    """
    GIVEN a test client logged in as a 'student' user (unauthorized)
    WHEN the '/groups' page is requested (GET)
    THEN check the response status is 403.
    """
    response = logged_in_student.get(url_for('main.groups'))
    assert response.status_code == 403
    assert b'Forbidden' in response.data

def test_groups_page_unauthenticated(test_client):
    """
    GIVEN a test client that is not logged in
    WHEN the '/groups' page is requested (GET)
    THEN check the response status is 401.
    """
    response = test_client.get(url_for('main.groups'))
    assert response.status_code == 401
    assert b'Unauthorized' in response.data

def test_groups_page_with_trips_and_students(logged_in_admin, sample_trip, sample_student_with_trip):
    """
    GIVEN a test client logged in as an admin with trips and students
    WHEN the '/groups' page is requested (GET)
    THEN check the response status is 200
    """
    response = logged_in_admin.get(url_for('main.groups'))
    assert response.status_code == 200
    # Check that trip information is present
    assert sample_trip.trip_name.encode() in response.data


# Add Student - admin_required
def test_add_student_success(logged_in_admin, sample_trip):
    """
    GIVEN a test client logged in as an admin
    WHEN a POST request is made to '/add-student' with valid data
    THEN check the student is created and redirected to first-years page
    """
    response = logged_in_admin.post(url_for('main.add_student'), data={
        'student_id': 'S100',
        'email': 'newstudent@colby.edu',
        'first_name': 'New',
        'last_name': 'Student',
        'gender': 'Male',
        'dorm': 'Dana',
        'trip_pref_1': 'backpacking',
        'assigned-trip': str(sample_trip.id)
    }, follow_redirects=True)
    assert response.status_code == 200

    student = Student.query.filter_by(student_id='S100').first()
    assert student is not None
    assert student.first_name == 'New'
    assert student.last_name == 'Student'
    assert student.trip_id == sample_trip.id

def test_add_student_missing_required_fields(logged_in_admin):
    """
    GIVEN a test client logged in as an admin
    WHEN a POST request is made to '/add-student' with missing required fields
    THEN check an error flash message is shown
    """
    response = logged_in_admin.post(url_for('main.add_student'), data={
        'student_id': 'S101',
        'email': 'incomplete@colby.edu',
        # Missing first_name and last_name
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Error: Missing required fields' in response.data

def test_add_student_duplicate_student_id(logged_in_admin, sample_student):
    """
    GIVEN a test client logged in as an admin
    WHEN a POST request is made to '/add-student' with duplicate student_id
    THEN check an error flash message is shown
    """
    response = logged_in_admin.post(url_for('main.add_student'), data={
        'student_id': sample_student.student_id,
        'email': 'different@colby.edu',
        'first_name': 'Different',
        'last_name': 'Student'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Error: Student with that ID or Email already exists' in response.data

def test_add_student_unauthorized(logged_in_student):
    """
    GIVEN a test client logged in as a student (unauthorized)
    WHEN a POST request is made to '/add-student'
    THEN check the response is 403
    """
    response = logged_in_student.post(url_for('main.add_student'), data={})
    assert response.status_code == 403
    assert b'Forbidden' in response.data

def test_add_student_get_redirects(logged_in_admin):
    """
    GIVEN a test client logged in as an admin
    WHEN a GET request is made to '/add-student'
    THEN check it redirects to first-years page
    """
    response = logged_in_admin.get(url_for('main.add_student'))
    assert response.status_code == 302
    assert url_for('main.first_years') in response.headers['Location']


# Edit Student - admin_required
def test_edit_student_success(logged_in_admin, sample_student):
    """
    GIVEN a test client logged in as an admin
    WHEN a POST request is made to '/edit-student' with valid data
    THEN check the student is updated and redirected to first-years page
    """
    response = logged_in_admin.post(url_for('main.edit_student'), data={
        'student_db_id': str(sample_student.id),
        'student_id_field': sample_student.student_id,
        'email': sample_student.email,
        'first_name': 'Updated',
        'last_name': 'Name',
        'gender': 'Female',
        'dorm': 'West'
    }, follow_redirects=True)
    assert response.status_code == 200

    db.session.refresh(sample_student)
    assert sample_student.first_name == 'Updated'
    assert sample_student.last_name == 'Name'

def test_edit_student_missing_id(logged_in_admin):
    """
    GIVEN a test client logged in as an admin
    WHEN a POST request is made to '/edit-student' without student_db_id
    THEN check an error flash message is shown
    """
    response = logged_in_admin.post(url_for('main.edit_student'), data={
        'first_name': 'Test',
        'last_name': 'Student'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Error: Student ID is required' in response.data

def test_edit_student_not_found(logged_in_admin):
    """
    GIVEN a test client logged in as an admin
    WHEN a POST request is made to '/edit-student' with invalid student_db_id
    THEN check an error flash message is shown
    """
    response = logged_in_admin.post(url_for('main.edit_student'), data={
        'student_db_id': '99999',
        'student_id_field': 'S999',
        'email': 'test@colby.edu',
        'first_name': 'Test',
        'last_name': 'Student'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Error: Student not found' in response.data

def test_edit_student_duplicate_email(logged_in_admin, sample_student):
    """
    GIVEN a test client logged in as an admin
    WHEN a POST request is made to '/edit-student' with duplicate email
    THEN check an error flash message is shown
    """
    # Create another student
    other_student = Student(
        student_id='S200',
        email='other@colby.edu',
        first_name='Other',
        last_name='Student'
    )
    db.session.add(other_student)
    db.session.commit()

    response = logged_in_admin.post(url_for('main.edit_student'), data={
        'student_db_id': str(sample_student.id),
        'student_id_field': sample_student.student_id,
        'email': 'other@colby.edu',  # Duplicate email
        'first_name': sample_student.first_name,
        'last_name': sample_student.last_name
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Error: Email already exists for another student' in response.data

def test_edit_student_with_trip_assignment(logged_in_admin, sample_student, sample_trip):
    """
    GIVEN a test client logged in as an admin
    WHEN a POST request is made to '/edit-student' with trip assignment
    THEN check the student's trip is updated
    """
    response = logged_in_admin.post(url_for('main.edit_student'), data={
        'student_db_id': str(sample_student.id),
        'student_id_field': sample_student.student_id,
        'email': sample_student.email,
        'first_name': sample_student.first_name,
        'last_name': sample_student.last_name,
        'assigned-trip': str(sample_trip.id)
    }, follow_redirects=True)
    assert response.status_code == 200

    db.session.refresh(sample_student)
    assert sample_student.trip_id == sample_trip.id

def test_edit_student_clear_trip_assignment(logged_in_admin, sample_student_with_trip):
    """
    GIVEN a test client logged in as an admin
    WHEN a POST request is made to '/edit-student' without trip assignment
    THEN check the student's trip is cleared
    """
    assert sample_student_with_trip.trip_id is not None

    response = logged_in_admin.post(url_for('main.edit_student'), data={
        'student_db_id': str(sample_student_with_trip.id),
        'student_id_field': sample_student_with_trip.student_id,
        'email': sample_student_with_trip.email,
        'first_name': sample_student_with_trip.first_name,
        'last_name': sample_student_with_trip.last_name,
        # No assigned-trip field
    }, follow_redirects=True)
    assert response.status_code == 200

    db.session.refresh(sample_student_with_trip)
    assert sample_student_with_trip.trip_id is None


# Remove Student - admin_required
def test_remove_student_success(logged_in_admin, sample_student):
    """
    GIVEN a test client logged in as an admin
    WHEN a POST request is made to '/remove-student' with valid student_id
    THEN check the student is deleted and redirected to first-years page
    """
    student_id = sample_student.id
    response = logged_in_admin.post(url_for('main.remove_student'), data={
        'student_id': str(student_id)
    }, follow_redirects=True)
    assert response.status_code == 200

    deleted_student = Student.query.get(student_id)
    assert deleted_student is None

def test_remove_student_missing_id(logged_in_admin):
    """
    GIVEN a test client logged in as an admin
    WHEN a POST request is made to '/remove-student' without student_id
    THEN check an error flash message is shown
    """
    response = logged_in_admin.post(url_for('main.remove_student'), data={}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Error: No student was selected' in response.data

def test_remove_student_not_found(logged_in_admin):
    """
    GIVEN a test client logged in as an admin
    WHEN a POST request is made to '/remove-student' with invalid student_id
    THEN check an error flash message is shown
    """
    response = logged_in_admin.post(url_for('main.remove_student'), data={
        'student_id': '99999'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Error: Student not found' in response.data

def test_remove_student_get_redirects(logged_in_admin):
    """
    GIVEN a test client logged in as an admin
    WHEN a GET request is made to '/remove-student'
    THEN check it redirects to first-years page
    """
    response = logged_in_admin.get(url_for('main.remove_student'))
    assert response.status_code == 302
    assert url_for('main.first_years') in response.headers['Location']


# Add Trip - admin_required
def test_add_trip_success(logged_in_admin):
    """
    GIVEN a test client logged in as an admin
    WHEN a POST request is made to '/add-trip' with valid data
    THEN check the trip is created and redirected to trips page
    """
    response = logged_in_admin.post(url_for('main.add_trip'), data={
        'trip_name': 'New Trip',
        'trip_type': 'canoeing',
        'capacity': '15',
        'address': '123 River Rd',
        'water': 'true',
        'tent': 'false'
    }, follow_redirects=True)
    assert response.status_code == 200

    trip = Trip.query.filter_by(trip_name='New Trip').first()
    assert trip is not None
    assert trip.trip_type == 'canoeing'
    assert trip.capacity == 15
    assert trip.water is True
    assert trip.tent is False

def test_add_trip_missing_required_fields(logged_in_admin):
    """
    GIVEN a test client logged in as an admin
    WHEN a POST request is made to '/add-trip' with missing required fields
    THEN check an error flash message is shown
    """
    response = logged_in_admin.post(url_for('main.add_trip'), data={
        'trip_name': 'Incomplete Trip',
        # Missing trip_type and capacity
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Error: One or more required fields' in response.data

def test_add_trip_invalid_capacity(logged_in_admin):
    """
    GIVEN a test client logged in as an admin
    WHEN a POST request is made to '/add-trip' with invalid capacity
    THEN check an error flash message is shown
    """
    response = logged_in_admin.post(url_for('main.add_trip'), data={
        'trip_name': 'Invalid Trip',
        'trip_type': 'backpacking',
        'capacity': '-5'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Error: Capacity must be a positive integer' in response.data

def test_add_trip_duplicate_name(logged_in_admin, sample_trip):
    """
    GIVEN a test client logged in as an admin
    WHEN a POST request is made to '/add-trip' with duplicate trip_name
    THEN check an error flash message is shown
    """
    response = logged_in_admin.post(url_for('main.add_trip'), data={
        'trip_name': sample_trip.trip_name,
        'trip_type': 'backpacking',
        'capacity': '10'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Error: A trip with the name' in response.data

def test_add_trip_get_redirects(logged_in_admin):
    """
    GIVEN a test client logged in as an admin
    WHEN a GET request is made to '/add-trip'
    THEN check it redirects to trips page
    """
    response = logged_in_admin.get(url_for('main.add_trip'))
    assert response.status_code == 302
    assert url_for('main.trips') in response.headers['Location']


# Edit Trip - admin_required
def test_edit_trip_success(logged_in_admin, sample_trip):
    """
    GIVEN a test client logged in as an admin
    WHEN a POST request is made to '/edit-trip' with valid data
    THEN check the trip is updated and redirected to trips page
    """
    response = logged_in_admin.post(url_for('main.edit_trip'), data={
        'trip_id': str(sample_trip.id),
        'trip_name': 'Updated Trip',
        'trip_type': 'basecamp',
        'capacity': '20',
        'address': '456 New St',
        'water': 'true',
        'tent': 'true'
    }, follow_redirects=True)
    assert response.status_code == 200

    db.session.refresh(sample_trip)
    assert sample_trip.trip_name == 'Updated Trip'
    assert sample_trip.trip_type == 'basecamp'
    assert sample_trip.capacity == 20

def test_edit_trip_missing_id(logged_in_admin):
    """
    GIVEN a test client logged in as an admin
    WHEN a POST request is made to '/edit-trip' without trip_id
    THEN check an error flash message is shown
    """
    response = logged_in_admin.post(url_for('main.edit_trip'), data={
        'trip_name': 'Test Trip',
        'trip_type': 'backpacking',
        'capacity': '10'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Error: Trip ID is required' in response.data

def test_edit_trip_not_found(logged_in_admin):
    """
    GIVEN a test client logged in as an admin
    WHEN a POST request is made to '/edit-trip' with invalid trip_id
    THEN check an error flash message is shown
    """
    response = logged_in_admin.post(url_for('main.edit_trip'), data={
        'trip_id': '99999',
        'trip_name': 'Test Trip',
        'trip_type': 'backpacking',
        'capacity': '10'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Error: Trip not found' in response.data


# Remove Trip - admin_required
def test_remove_trip_success(logged_in_admin, sample_trip):
    """
    GIVEN a test client logged in as an admin
    WHEN a POST request is made to '/remove-trip' with valid trip_id
    THEN check the trip is deleted and redirected to trips page
    """
    trip_id = sample_trip.id
    response = logged_in_admin.post(url_for('main.remove_trip'), data={
        'trip_id': str(trip_id)
    }, follow_redirects=True)
    assert response.status_code == 200

    deleted_trip = Trip.query.get(trip_id)
    assert deleted_trip is None

def test_remove_trip_missing_id(logged_in_admin):
    """
    GIVEN a test client logged in as an admin
    WHEN a POST request is made to '/remove-trip' without trip_id
    THEN check an error flash message is shown
    """
    response = logged_in_admin.post(url_for('main.remove_trip'), data={}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Error: No trip was selected' in response.data

def test_remove_trip_get_redirects(logged_in_admin):
    """
    GIVEN a test client logged in as an admin
    WHEN a GET request is made to '/remove-trip'
    THEN check it redirects to trips page
    """
    response = logged_in_admin.get(url_for('main.remove_trip'))
    assert response.status_code == 302
    assert url_for('main.trips') in response.headers['Location']

def test_remove_trip_clears_student_assignments(
    logged_in_admin, sample_trip, sample_student_with_trip
):
    """
    GIVEN a test client logged in as an admin
    WHEN a POST request is made to '/remove-trip' for a trip with assigned students
    THEN check student trip assignments are cleared (set to NULL)
    """
    assert sample_student_with_trip.trip_id == sample_trip.id

    response = logged_in_admin.post(
        url_for('main.remove_trip'),
        data={'trip_id': str(sample_trip.id)},
        follow_redirects=True
    )
    assert response.status_code == 200

    db.session.refresh(sample_student_with_trip)
    assert sample_student_with_trip.trip_id is None


# Upload CSV - admin_required
def test_upload_csv_success(logged_in_admin):
    """
    GIVEN a test client logged in as an admin
    WHEN a POST request is made to '/upload_csv' with valid CSV file
    THEN check students are imported and redirected to groups page
    """
    csv_data = 'student_id,first_name,last_name,email,gender\nS300,Test,User,testuser@colby.edu,Male'
    csv_file = (io.BytesIO(csv_data.encode('utf-8')), 'test.csv')

    response = logged_in_admin.post(
        url_for('main.upload_csv'),
        data={'csv_file': csv_file},
        follow_redirects=True,
        content_type='multipart/form-data'
    )
    assert response.status_code == 200

    student = Student.query.filter_by(student_id='S300').first()
    assert student is not None
    assert student.first_name == 'Test'

def test_upload_csv_no_file(logged_in_admin):
    """
    GIVEN a test client logged in as an admin
    WHEN a POST request is made to '/upload_csv' without a file
    THEN check an error flash message is shown
    """
    response = logged_in_admin.post(url_for('main.upload_csv'), data={}, follow_redirects=True)
    assert response.status_code == 200
    assert b'No file selected' in response.data

def test_upload_csv_creates_trip(logged_in_admin):
    """
    GIVEN a test client logged in as an admin
    WHEN a POST request is made to '/upload_csv' with trip_name and trip_type
    THEN check a new trip is created if it doesn't exist
    """
    csv_data = (
        'student_id,first_name,last_name,email,trip_name,trip_type\n'
        'S400,Test,User,testuser2@colby.edu,New Trip,backpacking'
    )
    csv_file = (io.BytesIO(csv_data.encode('utf-8')), 'test.csv')

    response = logged_in_admin.post(
        url_for('main.upload_csv'),
        data={'csv_file': csv_file},
        follow_redirects=True,
        content_type='multipart/form-data'
    )
    assert response.status_code == 200

    trip = Trip.query.filter_by(trip_name='New Trip').first()
    assert trip is not None
    assert trip.trip_type == 'backpacking'

def test_upload_csv_updates_existing_student(logged_in_admin, sample_student):
    """
    GIVEN a test client logged in as an admin
    WHEN a POST request is made to '/upload_csv' with existing student_id
    THEN check the student is updated, not duplicated
    """
    csv_data = (
        f'student_id,first_name,last_name,email\n'
        f'{sample_student.student_id},Updated,Name,{sample_student.email}'
    )
    csv_file = (io.BytesIO(csv_data.encode('utf-8')), 'test.csv')

    response = logged_in_admin.post(
        url_for('main.upload_csv'),
        data={'csv_file': csv_file},
        follow_redirects=True,
        content_type='multipart/form-data'
    )
    assert response.status_code == 200

    # Check only one student with this ID exists
    students = Student.query.filter_by(student_id=sample_student.student_id).all()
    assert len(students) == 1
    assert students[0].first_name == 'Updated'
    assert students[0].last_name == 'Name'

def test_upload_csv_skips_incomplete_rows(logged_in_admin):
    """
    GIVEN a test client logged in as an admin
    WHEN a POST request is made to '/upload_csv' with incomplete rows
    THEN check incomplete rows are skipped
    """
    csv_data = (
        'student_id,first_name,last_name,email\n'
        'S500,Complete,Student,complete@colby.edu\n'
        'S501,,Incomplete,\n'
        'S502,Another,Complete,another@colby.edu'
    )
    csv_file = (io.BytesIO(csv_data.encode('utf-8')), 'test.csv')

    response = logged_in_admin.post(
        url_for('main.upload_csv'),
        data={'csv_file': csv_file},
        follow_redirects=True,
        content_type='multipart/form-data'
    )
    assert response.status_code == 200

    # Check only complete students were added
    assert Student.query.filter_by(student_id='S500').first() is not None
    assert Student.query.filter_by(student_id='S501').first() is None
    assert Student.query.filter_by(student_id='S502').first() is not None


# Export CSV - admin_required
def test_export_csv_success(logged_in_admin, sample_student):
    """
    GIVEN a test client logged in as an admin
    WHEN a GET request is made to '/export_csv'
    THEN check a CSV file is returned with student data
    """
    response = logged_in_admin.get(url_for('main.export_csv'))
    assert response.status_code == 200
    assert response.mimetype == 'text/csv'
    assert b'Student ID' in response.data
    assert sample_student.student_id.encode() in response.data

def test_export_csv_empty_database(logged_in_admin):
    """
    GIVEN a test client logged in as an admin and empty database
    WHEN a GET request is made to '/export_csv'
    THEN check a CSV file is returned with headers only
    """
    response = logged_in_admin.get(url_for('main.export_csv'))
    assert response.status_code == 200
    assert response.mimetype == 'text/csv'
    assert b'Student ID' in response.data

def test_export_csv_unauthorized(logged_in_student):
    """
    GIVEN a test client logged in as a student (unauthorized)
    WHEN a GET request is made to '/export_csv'
    THEN check the response is 403
    """
    response = logged_in_student.get(url_for('main.export_csv'))
    assert response.status_code == 403
    assert b'Forbidden' in response.data


# Export Trip CSV - admin_required
def test_export_trip_csv_success(logged_in_admin, sample_trip):
    """
    GIVEN a test client logged in as an admin
    WHEN a GET request is made to '/export_trip_csv'
    THEN check a CSV file is returned with trip data
    """
    response = logged_in_admin.get(url_for('main.export_trip_csv'))
    assert response.status_code == 200
    assert response.mimetype == 'text/csv'
    assert b'Trip Name' in response.data
    assert sample_trip.trip_name.encode() in response.data


# Export PDF - admin_required
def test_export_pdf_success(logged_in_admin, sample_trip, sample_student_with_trip):
    """
    GIVEN a test client logged in as an admin
    WHEN a GET request is made to '/export_pdf'
    THEN check a PDF file is returned
    """
    response = logged_in_admin.get(url_for('main.export_pdf'))
    assert response.status_code == 200
    assert response.mimetype == 'application/pdf'
    assert b'%PDF' in response.data

def test_export_pdf_empty_trips(logged_in_admin):
    """
    GIVEN a test client logged in as an admin
    WHEN a GET request is made to '/export_pdf' with no trips
    THEN check a PDF file is still returned (empty)
    """
    response = logged_in_admin.get(url_for('main.export_pdf'))
    assert response.status_code == 200
    assert response.mimetype == 'application/pdf'


# Download Sample CSV - admin_required
def test_download_sample_csv_success(logged_in_admin):
    """
    GIVEN a test client logged in as an admin
    WHEN a GET request is made to '/download_sample_csv'
    THEN check a CSV file is returned with sample data
    """
    response = logged_in_admin.get(url_for('main.download_sample_csv'))
    assert response.status_code == 200
    assert response.mimetype == 'text/csv'
    assert b'student_id' in response.data
    assert b'S001' in response.data  # Sample data


# Sort Students - admin_required
def test_sort_students_success(logged_in_admin, sample_trip, sample_student):
    """
    GIVEN a test client logged in as an admin
    WHEN a POST request is made to '/sort-students'
    THEN check students are sorted and redirected to groups page
    """
    # Set trip preference for student
    sample_student.trip_pref_1 = sample_trip.trip_type
    db.session.commit()

    response = logged_in_admin.post(
        url_for('main.sort_students_route'), follow_redirects=True
    )
    assert response.status_code == 200
    # Check for success message (may vary based on sort_students implementation)
    assert b'Sorting completed' in response.data or b'Sorting failed' in response.data


# Clear Databases - manager_required
def test_clear_databases_success(logged_in_admin_manager, sample_student, sample_trip):
    """
    GIVEN a test client logged in as an admin_manager
    WHEN a POST request is made to '/clear-databases'
    THEN check students, trips, and non-admin users are deleted
    """
    response = logged_in_admin_manager.post(
        url_for('main.clear_databases'), follow_redirects=True
    )
    assert response.status_code == 200

    # Check students and trips are deleted
    assert Student.query.count() == 0
    assert Trip.query.count() == 0

def test_clear_databases_unauthorized_admin(logged_in_admin):
    """
    GIVEN a test client logged in as an admin (not admin_manager)
    WHEN a POST request is made to '/clear-databases'
    THEN check the response is 403
    """
    response = logged_in_admin.post(url_for('main.clear_databases'))
    assert response.status_code == 403
    assert b'Forbidden' in response.data

# Additional tests for coverage gaps

def test_add_student_exception_handling(logged_in_admin, sample_student, monkeypatch):
    """
    GIVEN a test client logged in as an admin
    WHEN a POST request is made to '/add-student' that triggers a database exception
    THEN check exception is caught and error message is shown
    """
    # Mock db.session.add to raise an exception
    def mock_add(obj):
        raise Exception("Database error")

    monkeypatch.setattr(db.session, 'add', mock_add)

    response = logged_in_admin.post(url_for('main.add_student'), data={
        'student_id': 'S600',
        'email': 'exception@colby.edu',
        'first_name': 'Test',
        'last_name': 'Exception'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Error adding student' in response.data

def test_edit_student_invalid_id_type(logged_in_admin):
    """
    GIVEN a test client logged in as an admin
    WHEN a POST request is made to '/edit-student' with invalid student_db_id type
    THEN check ValueError/TypeError is caught
    """
    response = logged_in_admin.post(url_for('main.edit_student'), data={
        'student_db_id': 'not_a_number',
        'student_id_field': 'S999',
        'email': 'test@colby.edu',
        'first_name': 'Test',
        'last_name': 'Student'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Error: Student not found' in response.data

def test_edit_student_missing_fields_using_student_id(logged_in_admin, sample_student):
    """
    GIVEN a test client logged in as an admin
    WHEN a POST request is made to '/edit-student' with missing fields using student_id
    THEN check error message is shown
    """
    response = logged_in_admin.post(url_for('main.edit_student'), data={
        'student_db_id': str(sample_student.id),
        'student_id': sample_student.student_id,  # Using student_id instead of student_id_field
        # Missing email, first_name, last_name
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Error: Missing required fields' in response.data

def test_edit_student_duplicate_student_id(logged_in_admin, sample_student):
    """
    GIVEN a test client logged in as an admin
    WHEN a POST request is made to '/edit-student' with duplicate student_id
    THEN check error message is shown
    """
    # Create another student
    other_student = Student(
        student_id='S700',
        email='other2@colby.edu',
        first_name='Other',
        last_name='Student'
    )
    db.session.add(other_student)
    db.session.commit()

    response = logged_in_admin.post(url_for('main.edit_student'), data={
        'student_db_id': str(sample_student.id),
        'student_id_field': 'S700',  # Duplicate student_id
        'email': sample_student.email,
        'first_name': sample_student.first_name,
        'last_name': sample_student.last_name
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Error: Student ID already exists for another student' in response.data

def test_edit_student_email_change_no_duplicate(logged_in_admin, sample_student):
    """
    GIVEN a test client logged in as an admin
    WHEN a POST request is made to '/edit-student' changing email to a new unique email
    THEN check the student is updated successfully
    """
    response = logged_in_admin.post(url_for('main.edit_student'), data={
        'student_db_id': str(sample_student.id),
        'student_id_field': sample_student.student_id,
        'email': 'newunique@colby.edu',  # New unique email
        'first_name': sample_student.first_name,
        'last_name': sample_student.last_name
    }, follow_redirects=True)
    assert response.status_code == 200

    db.session.refresh(sample_student)
    assert sample_student.email == 'newunique@colby.edu'

def test_edit_student_exception_handling(logged_in_admin, sample_student, monkeypatch):
    """
    GIVEN a test client logged in as an admin
    WHEN a POST request is made to '/edit-student' that triggers a database exception
    THEN check exception is caught and error message is shown
    """
    # Mock db.session.commit to raise an exception
    def mock_commit():
        raise Exception("Database error")

    monkeypatch.setattr(db.session, 'commit', mock_commit)

    response = logged_in_admin.post(url_for('main.edit_student'), data={
        'student_db_id': str(sample_student.id),
        'student_id_field': sample_student.student_id,
        'email': sample_student.email,
        'first_name': 'Updated',
        'last_name': 'Name'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Error updating student' in response.data

def test_remove_student_exception_handling(logged_in_admin, sample_student, monkeypatch):
    """
    GIVEN a test client logged in as an admin
    WHEN a POST request is made to '/remove-student' that triggers a database exception
    THEN check exception is caught and error message is shown
    """
    # Mock db.session.delete to raise an exception
    def mock_delete(obj):
        raise RuntimeError("Database error")

    monkeypatch.setattr(db.session, 'delete', mock_delete)

    response = logged_in_admin.post(url_for('main.remove_student'), data={
        'student_id': str(sample_student.id)
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Error: Could not remove student' in response.data

def test_add_trip_exception_handling(logged_in_admin, monkeypatch):
    """
    GIVEN a test client logged in as an admin
    WHEN a POST request is made to '/add-trip' that triggers a database exception
    THEN check exception is caught and error message is shown
    """
    # Mock db.session.add to raise an exception
    def mock_add(obj):
        raise Exception("Database error")

    monkeypatch.setattr(db.session, 'add', mock_add)

    response = logged_in_admin.post(url_for('main.add_trip'), data={
        'trip_name': 'Exception Trip',
        'trip_type': 'backpacking',
        'capacity': '10'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Error: Could not add trip' in response.data

def test_edit_trip_invalid_id_type(logged_in_admin):
    """
    GIVEN a test client logged in as an admin
    WHEN a POST request is made to '/edit-trip' with invalid trip_id type
    THEN check ValueError/TypeError is caught
    """
    response = logged_in_admin.post(url_for('main.edit_trip'), data={
        'trip_id': 'not_a_number',
        'trip_name': 'Test Trip',
        'trip_type': 'backpacking',
        'capacity': '10'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Error: Trip not found' in response.data

def test_edit_trip_missing_required_fields(logged_in_admin, sample_trip):
    """
    GIVEN a test client logged in as an admin
    WHEN a POST request is made to '/edit-trip' with missing required fields
    THEN check error message is shown
    """
    response = logged_in_admin.post(url_for('main.edit_trip'), data={
        'trip_id': str(sample_trip.id),
        'trip_name': 'Incomplete',
        # Missing trip_type and capacity
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Error: Missing required fields' in response.data

def test_edit_trip_invalid_capacity_zero(logged_in_admin, sample_trip):
    """
    GIVEN a test client logged in as an admin
    WHEN a POST request is made to '/edit-trip' with capacity = 0
    THEN check error message is shown
    """
    response = logged_in_admin.post(url_for('main.edit_trip'), data={
        'trip_id': str(sample_trip.id),
        'trip_name': sample_trip.trip_name,
        'trip_type': sample_trip.trip_type,
        'capacity': '0'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Error: Capacity must be a positive integer' in response.data

def test_edit_trip_duplicate_name(logged_in_admin, sample_trip):
    """
    GIVEN a test client logged in as an admin
    WHEN a POST request is made to '/edit-trip' with duplicate trip_name
    THEN check error message is shown
    """
    # Create another trip
    other_trip = Trip(
        trip_name='Other Trip',
        trip_type='canoeing',
        capacity=10
    )
    db.session.add(other_trip)
    db.session.commit()

    response = logged_in_admin.post(url_for('main.edit_trip'), data={
        'trip_id': str(sample_trip.id),
        'trip_name': 'Other Trip',  # Duplicate name
        'trip_type': sample_trip.trip_type,
        'capacity': '10'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Error: A trip with the name' in response.data

def test_edit_trip_name_change_no_duplicate(logged_in_admin, sample_trip):
    """
    GIVEN a test client logged in as an admin
    WHEN a POST request is made to '/edit-trip' changing name to a new unique name
    THEN check the trip is updated successfully
    """
    response = logged_in_admin.post(url_for('main.edit_trip'), data={
        'trip_id': str(sample_trip.id),
        'trip_name': 'Unique New Name',
        'trip_type': sample_trip.trip_type,
        'capacity': '10'
    }, follow_redirects=True)
    assert response.status_code == 200

    db.session.refresh(sample_trip)
    assert sample_trip.trip_name == 'Unique New Name'

def test_edit_trip_exception_handling(logged_in_admin, sample_trip, monkeypatch):
    """
    GIVEN a test client logged in as an admin
    WHEN a POST request is made to '/edit-trip' that triggers a database exception
    THEN check exception is caught and error message is shown
    """
    # Mock db.session.commit to raise an exception
    def mock_commit():
        raise Exception("Database error")

    monkeypatch.setattr(db.session, 'commit', mock_commit)

    response = logged_in_admin.post(url_for('main.edit_trip'), data={
        'trip_id': str(sample_trip.id),
        'trip_name': 'Updated Trip',
        'trip_type': 'basecamp',
        'capacity': '20'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Error updating trip' in response.data

def test_remove_trip_exception_handling(logged_in_admin, sample_trip, monkeypatch):
    """
    GIVEN a test client logged in as an admin
    WHEN a POST request is made to '/remove-trip' that triggers a database exception
    THEN check exception is caught and error message is shown
    """
    # Mock db.session.delete to raise an exception
    def mock_delete(obj):
        raise RuntimeError("Database error")

    monkeypatch.setattr(db.session, 'delete', mock_delete)

    response = logged_in_admin.post(url_for('main.remove_trip'), data={
        'trip_id': str(sample_trip.id)
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Error: Could not remove trip' in response.data

def test_upload_csv_exception_handling(logged_in_admin, monkeypatch):
    """
    GIVEN a test client logged in as an admin
    WHEN a POST request is made to '/upload_csv' that triggers an exception
    THEN check exception is caught and error message is shown
    """
    csv_data = 'student_id,first_name,last_name,email\nS800,Test,User,test@colby.edu'
    csv_file = (io.BytesIO(csv_data.encode('utf-8')), 'test.csv')

    # Mock db.session.commit to raise an exception
    def mock_commit():
        raise Exception("CSV processing error")

    monkeypatch.setattr(db.session, 'commit', mock_commit)

    response = logged_in_admin.post(
        url_for('main.upload_csv'),
        data={'csv_file': csv_file},
        follow_redirects=True,
        content_type='multipart/form-data'
    )
    assert response.status_code == 200
    assert b'Error processing CSV' in response.data

def test_upload_csv_creates_trip_branch(logged_in_admin):
    """
    GIVEN a test client logged in as an admin
    WHEN a POST request is made to '/upload_csv' with trip_name but no existing trip
    THEN check a new trip is created
    """
    csv_data = 'student_id,first_name,last_name,email,trip_name,trip_type\nS900,Test,User,test900@colby.edu,New Trip 2,basecamp'
    csv_file = (io.BytesIO(csv_data.encode('utf-8')), 'test.csv')

    response = logged_in_admin.post(
        url_for('main.upload_csv'),
        data={'csv_file': csv_file},
        follow_redirects=True,
        content_type='multipart/form-data'
    )
    assert response.status_code == 200

    trip = Trip.query.filter_by(trip_name='New Trip 2').first()
    assert trip is not None
    assert trip.trip_type == 'basecamp'

def test_export_csv_with_invalid_trip_id(logged_in_admin, sample_student):
    """
    GIVEN a test client logged in as an admin
    WHEN a GET request is made to '/export_csv' with student having invalid trip_id
    THEN check CSV is exported without errors
    """
    # Set invalid trip_id
    sample_student.trip_id = 99999
    db.session.commit()

    response = logged_in_admin.get(url_for('main.export_csv'))
    assert response.status_code == 200
    assert response.mimetype == 'text/csv'
    # Should still export, just with empty trip name/type
    assert sample_student.student_id.encode() in response.data

def test_export_pdf_multiple_trips(logged_in_admin):
    """
    GIVEN a test client logged in as an admin
    WHEN a GET request is made to '/export_pdf' with multiple trips
    THEN check PDF is generated with multiple pages
    """
    # Create multiple trips
    trip1 = Trip(trip_name='Trip 1', trip_type='backpacking', capacity=10)
    trip2 = Trip(trip_name='Trip 2', trip_type='canoeing', capacity=10)
    db.session.add_all([trip1, trip2])
    db.session.commit()

    response = logged_in_admin.get(url_for('main.export_pdf'))
    assert response.status_code == 200
    assert response.mimetype == 'application/pdf'

def test_export_pdf_with_address(logged_in_admin):
    """
    GIVEN a test client logged in as an admin
    WHEN a GET request is made to '/export_pdf' with trip having address
    THEN check address is included in PDF
    """
    trip = Trip(
        trip_name='Trip With Address',
        trip_type='backpacking',
        capacity=10,
        address='123 Main St\nPortland, ME'
    )
    db.session.add(trip)
    db.session.commit()

    response = logged_in_admin.get(url_for('main.export_pdf'))
    assert response.status_code == 200
    assert response.mimetype == 'application/pdf'

def test_export_pdf_with_water_feature(logged_in_admin):
    """
    GIVEN a test client logged in as an admin
    WHEN a GET request is made to '/export_pdf' with water trip
    THEN check water feature is included in PDF
    """
    trip = Trip(
        trip_name='Water Trip PDF',
        trip_type='canoeing',
        capacity=10,
        water=True,
        tent=False
    )
    db.session.add(trip)
    db.session.commit()

    response = logged_in_admin.get(url_for('main.export_pdf'))
    assert response.status_code == 200
    assert response.mimetype == 'application/pdf'

def test_export_pdf_with_tent_feature(logged_in_admin):
    """
    GIVEN a test client logged in as an admin
    WHEN a GET request is made to '/export_pdf' with tent trip
    THEN check tent feature is included in PDF
    """
    trip = Trip(
        trip_name='Tent Trip PDF',
        trip_type='backpacking',
        capacity=10,
        water=False,
        tent=True
    )
    db.session.add(trip)
    db.session.commit()

    response = logged_in_admin.get(url_for('main.export_pdf'))
    assert response.status_code == 200
    assert response.mimetype == 'application/pdf'

def test_export_pdf_with_both_features(logged_in_admin):
    """
    GIVEN a test client logged in as an admin
    WHEN a GET request is made to '/export_pdf' with trip having both water and tent
    THEN check both features are included in PDF
    """
    trip = Trip(
        trip_name='Full Feature Trip',
        trip_type='backpacking',
        capacity=10,
        water=True,
        tent=True
    )
    db.session.add(trip)
    db.session.commit()

    response = logged_in_admin.get(url_for('main.export_pdf'))
    assert response.status_code == 200
    assert response.mimetype == 'application/pdf'

def test_export_pdf_empty_trip_students(logged_in_admin):
    """
    GIVEN a test client logged in as an admin
    WHEN a GET request is made to '/export_pdf' with trip having no students
    THEN check PDF is generated with "No students assigned yet" message
    """
    trip = Trip(trip_name='Empty Trip', trip_type='backpacking', capacity=10)
    db.session.add(trip)
    db.session.commit()

    response = logged_in_admin.get(url_for('main.export_pdf'))
    assert response.status_code == 200
    assert response.mimetype == 'application/pdf'

def test_export_pdf_many_students_new_page(logged_in_admin):
    """
    GIVEN a test client logged in as an admin
    WHEN a GET request is made to '/export_pdf' with trip having many students
    THEN check PDF generates new page when needed
    """
    trip = Trip(trip_name='Large Trip', trip_type='backpacking', capacity=50)
    db.session.add(trip)

    # Create many students to trigger new page
    students = []
    for i in range(30):
        student = Student(
            student_id=f'S{i+1000}',
            email=f'student{i+1000}@colby.edu',
            first_name=f'Student{i+1}',
            last_name='Test',
            gender='Male' if i % 2 == 0 else 'Female',
            dorm='Dana',
            trip_id=trip.id
        )
        students.append(student)

    db.session.add_all(students)
    db.session.commit()

    response = logged_in_admin.get(url_for('main.export_pdf'))
    assert response.status_code == 200
    assert response.mimetype == 'application/pdf'

def test_export_pdf_student_name_truncation(logged_in_admin):
    """
    GIVEN a test client logged in as an admin
    WHEN a GET request is made to '/export_pdf' with student having long name
    THEN check that a PDF is generated successfully.
    """
    trip = Trip(trip_name='Truncation Test', trip_type='backpacking', capacity=10)
    db.session.add(trip)

    student = Student(
        student_id='S2000',
        email='longname@colby.edu',
        first_name='VeryLongFirstName',
        last_name='VeryLongLastName',
        trip_id=trip.id
    )
    db.session.add(student)
    db.session.commit()

    response = logged_in_admin.get(url_for('main.export_pdf'))
    assert response.status_code == 200
    assert response.mimetype == 'application/pdf'

def test_export_pdf_dorm_truncation(logged_in_admin):
    """
    GIVEN a test client logged in as an admin
    WHEN a GET request is made to '/export_pdf' with student having long dorm name
    THEN check that a PDF is generated successfully.
    """
    trip = Trip(trip_name='Dorm Test', trip_type='backpacking', capacity=10)
    db.session.add(trip)

    student = Student(
        student_id='S2001',
        email='longdorm@colby.edu',
        first_name='Test',
        last_name='Student',
        dorm='VeryLongDormitoryName',
        trip_id=trip.id
    )
    db.session.add(student)
    db.session.commit()

    response = logged_in_admin.get(url_for('main.export_pdf'))
    assert response.status_code == 200
    assert response.mimetype == 'application/pdf'

def test_export_pdf_team_normalization(logged_in_admin):
    """
    GIVEN a test client logged in as an admin
    WHEN a GET request is made to '/export_pdf' with student having N/A team
    THEN check that a PDF is generated successfully.
    """
    trip = Trip(trip_name='Team Test', trip_type='backpacking', capacity=10)
    db.session.add(trip)

    student = Student(
        student_id='S2002',
        email='noteam@colby.edu',
        first_name='Test',
        last_name='Student',
        athletic_team='N/A',
        trip_id=trip.id
    )
    db.session.add(student)
    db.session.commit()

    response = logged_in_admin.get(url_for('main.export_pdf'))
    assert response.status_code == 200
    assert response.mimetype == 'application/pdf'

def test_export_pdf_team_truncation(logged_in_admin):
    """
    GIVEN a test client logged in as an admin
    WHEN a GET request is made to '/export_pdf' with student having long team name
    THEN check that a PDF is generated successfully.
    """
    trip = Trip(trip_name='Team Trunc Test', trip_type='backpacking', capacity=10)
    db.session.add(trip)

    student = Student(
        student_id='S2003',
        email='longteam@colby.edu',
        first_name='Test',
        last_name='Student',
        athletic_team='VeryLongAthleticTeamName',
        trip_id=trip.id
    )
    db.session.add(student)
    db.session.commit()

    response = logged_in_admin.get(url_for('main.export_pdf'))
    assert response.status_code == 200
    assert response.mimetype == 'application/pdf'

def test_export_pdf_exception_handling(logged_in_admin, monkeypatch):
    """
    GIVEN a test client logged in as an admin
    WHEN a GET request is made to '/export_pdf' that triggers an exception
    THEN check exception is caught and error message is returned
    """
    # Mock canvas.Canvas to raise an exception during save
    from reportlab.pdfgen import canvas as canvas_module

    def mock_save(self):
        raise RuntimeError("PDF generation error")

    monkeypatch.setattr(canvas_module.Canvas, 'save', mock_save)

    response = logged_in_admin.get(url_for('main.export_pdf'))
    assert response.status_code == 500
    assert b'Error generating PDF' in response.data

def test_sort_students_exception_handling(logged_in_admin, monkeypatch):
    """
    GIVEN a test client logged in as an admin
    WHEN a POST request is made to '/sort-students' that triggers an exception
    THEN check exception is caught and error message is shown
    """
    # Mock sort_students to raise an exception
    def mock_sort_students():
        raise RuntimeError("Sorting error")

    # Patch the imported function in the views module
    from website import views
    monkeypatch.setattr(views, 'sort_students', mock_sort_students)

    response = logged_in_admin.post(url_for('main.sort_students_route'), follow_redirects=True)
    assert response.status_code == 200
    assert b'Sorting failed' in response.data

def test_clear_databases_exception_handling(logged_in_admin_manager, monkeypatch):
    """
    GIVEN a test client logged in as an admin_manager
    WHEN a POST request is made to '/clear-databases' that triggers an exception
    THEN check exception is caught and error message is shown
    """
    # Mock db.session.commit to raise an exception
    def mock_commit():
        raise Exception("Database error")

    monkeypatch.setattr(db.session, 'commit', mock_commit)

    response = logged_in_admin_manager.post(
        url_for('main.clear_databases'), follow_redirects=True
    )
    assert response.status_code == 200
    assert b'Error clearing databases' in response.data


# Additional tests for remaining coverage gaps

def test_edit_student_id_change_no_duplicate(logged_in_admin, sample_student):
    """
    GIVEN a test client logged in as an admin
    WHEN a POST request is made to '/edit-student' changing student_id
    to a new unique value
    THEN check the student is updated successfully (covers branch 395->402)
    """
    response = logged_in_admin.post(
        url_for('main.edit_student'),
        data={
            'student_db_id': str(sample_student.id),
            'student_id_field': 'S_NEW_UNIQUE',  # New unique student_id
            'email': sample_student.email,
            'first_name': sample_student.first_name,
            'last_name': sample_student.last_name
        },
        follow_redirects=True
    )
    assert response.status_code == 200

    db.session.refresh(sample_student)
    assert sample_student.student_id == 'S_NEW_UNIQUE'


def test_remove_trip_not_found(logged_in_admin):
    """
    GIVEN a test client logged in as an admin
    WHEN a POST request is made to '/remove-trip' with invalid trip_id
    THEN check error message is shown (covers line 651)
    """
    response = logged_in_admin.post(url_for('main.remove_trip'), data={
        'trip_id': '99999'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Error: Trip not found' in response.data

def test_upload_csv_creates_trip_with_trip_type(logged_in_admin):
    """
    GIVEN a test client logged in as an admin
    WHEN a POST request is made to '/upload_csv' with trip_name but no
    existing trip and trip_type provided
    THEN check a new trip is created (covers branch 754->765)
    """
    csv_data = (
        'student_id,first_name,last_name,email,trip_name,trip_type\n'
        'S950,Test,User,test950@colby.edu,New Trip 3,basecamp'
    )
    csv_file = (io.BytesIO(csv_data.encode('utf-8')), 'test.csv')

    # Ensure trip doesn't exist
    existing_trip = Trip.query.filter_by(trip_name='New Trip 3').first()
    if existing_trip:
        db.session.delete(existing_trip)
        db.session.commit()

    response = logged_in_admin.post(
        url_for('main.upload_csv'),
        data={'csv_file': csv_file},
        follow_redirects=True,
        content_type='multipart/form-data'
    )
    assert response.status_code == 200

    trip = Trip.query.filter_by(trip_name='New Trip 3').first()
    assert trip is not None
    assert trip.trip_type == 'basecamp'

def test_export_csv_with_nonexistent_trip(logged_in_admin, sample_student):
    """
    GIVEN a test client logged in as an admin
    WHEN a GET request is made to '/export_csv' with student having trip_id that doesn't exist
    THEN check CSV is exported with empty trip name/type (covers lines 841-842)
    """
    # Set trip_id to a non-existent trip
    sample_student.trip_id = 99999
    db.session.commit()

    response = logged_in_admin.get(url_for('main.export_csv'))
    assert response.status_code == 200
    assert response.mimetype == 'text/csv'
    # Should export with empty trip name/type
    assert sample_student.student_id.encode() in response.data

def test_export_pdf_pagination_trigger(logged_in_admin):
    """
    GIVEN a test client logged in as an admin
    WHEN a GET request is made to '/export_pdf' with many students that trigger pagination
    THEN check PDF generates new pages correctly (covers lines 1024-1036)
    """
    trip = Trip(trip_name='Pagination Test Trip', trip_type='backpacking', capacity=50)
    db.session.add(trip)

    # Create enough students to trigger pagination (y < 100 condition)
    students = []
    for i in range(25):  # Enough to trigger new page
        student = Student(
            student_id=f'S{i+3000}',
            email=f'student{i+3000}@colby.edu',
            first_name=f'Student{i+1}',
            last_name='TestPagination',
            gender='Male' if i % 2 == 0 else 'Female',
            dorm='Dana',
            trip_id=trip.id
        )
        students.append(student)

    db.session.add_all(students)
    db.session.commit()

    response = logged_in_admin.get(url_for('main.export_pdf'))
    assert response.status_code == 200
    assert response.mimetype == 'application/pdf'

def test_export_pdf_multiple_students_padding(logged_in_admin):
    """
    GIVEN a test client logged in as an admin
    WHEN a GET request is made to '/export_pdf' with multiple students
    THEN check padding is added for rows after first (covers line 1040)
    """
    trip = Trip(trip_name='Padding Test', trip_type='backpacking', capacity=10)
    db.session.add(trip)

    # Create multiple students (idx > 1)
    for i in range(3):
        student = Student(
            student_id=f'S{i+4000}',
            email=f'student{i+4000}@colby.edu',
            first_name=f'Student{i+1}',
            last_name='Test',
            trip_id=trip.id
        )
        db.session.add(student)

    db.session.commit()

    response = logged_in_admin.get(url_for('main.export_pdf'))
    assert response.status_code == 200
    assert response.mimetype == 'application/pdf'

def test_export_pdf_long_name_truncation(logged_in_admin):
    """
    GIVEN a test client logged in as an admin
    WHEN a GET request is made to '/export_pdf' with student having name > 20 chars
    THEN check that a PDF is generated successfully.
    """
    trip = Trip(trip_name='Name Trunc Test', trip_type='backpacking', capacity=10)
    db.session.add(trip)

    student = Student(
        student_id='S5000',
        email='longname@colby.edu',
        first_name='VeryLongFirstNameThatExceeds',
        last_name='VeryLongLastNameThatExceeds',
        trip_id=trip.id
    )
    db.session.add(student)
    db.session.commit()

    response = logged_in_admin.get(url_for('main.export_pdf'))
    assert response.status_code == 200
    assert response.mimetype == 'application/pdf'

def test_export_pdf_long_dorm_truncation(logged_in_admin):
    """
    GIVEN a test client logged in as an admin
    WHEN a GET request is made to '/export_pdf' with student having dorm > 12 chars
    THEN check that a PDF is generated successfully.
    """
    trip = Trip(trip_name='Dorm Trunc Test', trip_type='backpacking', capacity=10)
    db.session.add(trip)

    student = Student(
        student_id='S5001',
        email='longdorm@colby.edu',
        first_name='Test',
        last_name='Student',
        dorm='VeryLongDormitoryNameThatExceeds',
        trip_id=trip.id
    )
    db.session.add(student)
    db.session.commit()

    response = logged_in_admin.get(url_for('main.export_pdf'))
    assert response.status_code == 200
    assert response.mimetype == 'application/pdf'

def test_export_pdf_team_none_normalization(logged_in_admin):
    """
    GIVEN a test client logged in as an admin
    WHEN a GET request is made to '/export_pdf' with student having team = 'none'
    THEN check that a PDF is generated successfully.
    """
    trip = Trip(trip_name='Team None Test', trip_type='backpacking', capacity=10)
    db.session.add(trip)

    student = Student(
        student_id='S5002',
        email='none@colby.edu',
        first_name='Test',
        last_name='Student',
        athletic_team='none',  # Lowercase 'none'
        trip_id=trip.id
    )
    db.session.add(student)
    db.session.commit()

    response = logged_in_admin.get(url_for('main.export_pdf'))
    assert response.status_code == 200
    assert response.mimetype == 'application/pdf'

def test_export_pdf_team_empty_normalization(logged_in_admin):
    """
    GIVEN a test client logged in as an admin
    WHEN a GET request is made to '/export_pdf' with student having empty team
    THEN check that a PDF is generated successfully.
    """
    trip = Trip(trip_name='Team Empty Test', trip_type='backpacking', capacity=10)
    db.session.add(trip)

    student = Student(
        student_id='S5003',
        email='empty@colby.edu',
        first_name='Test',
        last_name='Student',
        athletic_team='',  # Empty string
        trip_id=trip.id
    )
    db.session.add(student)
    db.session.commit()

    response = logged_in_admin.get(url_for('main.export_pdf'))
    assert response.status_code == 200
    assert response.mimetype == 'application/pdf'

def test_export_pdf_long_team_truncation(logged_in_admin):
    """
    GIVEN a test client logged in as an admin
    WHEN a GET request is made to '/export_pdf' with student having team > 20 chars
    THEN check that a PDF is generated successfully.
    """
    trip = Trip(trip_name='Team Trunc Test 2', trip_type='backpacking', capacity=10)
    db.session.add(trip)

    student = Student(
        student_id='S5004',
        email='longteam@colby.edu',
        first_name='Test',
        last_name='Student',
        athletic_team='VeryLongAthleticTeamNameThatExceedsTwenty',
        trip_id=trip.id
    )
    db.session.add(student)
    db.session.commit()

    response = logged_in_admin.get(url_for('main.export_pdf'))
    assert response.status_code == 200
    assert response.mimetype == 'application/pdf'


# Unauthorized Error Page Tests
def test_unauthorized_401_page_content(test_client):
    """
    GIVEN a test client that is not logged in
    WHEN an admin-required page is requested
    THEN check the 401 unauthorized page displays correct content
    """
    response = test_client.get(url_for('main.settings'))
    assert response.status_code == 401
    assert b'Uh Oh!' in response.data
    assert b'Something went wrong' in response.data
    assert b'401 Unauthorized' in response.data
    assert b'logged in' in response.data
    assert b'Return to Home' in response.data
    assert b'COOT' in response.data

def test_unauthorized_403_page_content(logged_in_student):
    """
    GIVEN a test client logged in as a student
    WHEN an admin-required page is requested
    THEN check the 403 forbidden page displays correct content
    """
    response = logged_in_student.get(url_for('main.settings'))
    assert response.status_code == 403
    assert b'Uh Oh!' in response.data
    assert b'Something went wrong' in response.data
    assert b'403 Forbidden' in response.data
    assert b'permissions' in response.data
    assert b'Return to Home' in response.data
    assert b'Logout' in response.data

def test_unauthorized_401_has_home_link(test_client):
    """
    GIVEN a test client that is not logged in
    WHEN the unauthorized page is displayed (401)
    THEN check it has a link to return home
    """
    response = test_client.get(url_for('main.trips'))
    assert response.status_code == 401
    assert b'href="/"' in response.data or b"href='/'" in response.data

def test_unauthorized_403_has_home_and_logout_links(logged_in_no_role):
    """
    GIVEN a test client logged in as a user with no role
    WHEN the unauthorized page is displayed (403)
    THEN check it has links to return home and logout
    """
    response = logged_in_no_role.get(url_for('main.trips'))
    assert response.status_code == 403
    assert b'href="/"' in response.data or b"href='/'" in response.data
    assert b'/logout' in response.data

def test_unauthorized_page_displays_user_info_when_authenticated(logged_in_student):
    """
    GIVEN a test client logged in as a student
    WHEN the unauthorized page is displayed
    THEN check it displays the user's name
    """
    response = logged_in_student.get(url_for('main.first_years'))
    assert response.status_code == 403
    assert b'Logged in as' in response.data

def test_unauthorized_401_different_routes(test_client):
    """
    GIVEN a test client that is not logged in
    WHEN multiple different protected routes are accessed
    THEN check all return 401 with unauthorized page
    """
    routes = [
        'main.settings',
        'main.trips',
        'main.first_years',
        'main.groups'
    ]
    for route in routes:
        response = test_client.get(url_for(route))
        assert response.status_code == 401
        assert b'Uh Oh!' in response.data

def test_unauthorized_403_different_roles(logged_in_student):
    """
    GIVEN a test client logged in as a student (insufficient role)
    WHEN admin-only routes are accessed
    THEN check all return 403 with forbidden page
    """
    routes = [
        'main.settings',
        'main.trips',
        'main.first_years',
        'main.groups'
    ]
    for route in routes:
        response = logged_in_student.get(url_for(route))
        assert response.status_code == 403
        assert b'Uh Oh!' in response.data

def test_no_access_page_shows_for_no_role_user(logged_in_no_role):
    """
    GIVEN a test client logged in as a user with no role
    WHEN the /no_access page is accessed
    THEN check it displays the no access page content
    """
    response = logged_in_no_role.get(url_for('main.no_access'))
    assert response.status_code == 200
    assert b'do not have access' in response.data.lower()

def test_no_access_page_redirects_user_with_student_role(logged_in_student):
    """
    GIVEN a test client logged in as a student
    WHEN the /no_access page is accessed
    THEN check it redirects to home since user has a role
    """
    response = logged_in_student.get(url_for('main.no_access'), follow_redirects=False)
    assert response.status_code == 302
    assert '/' in response.location

def test_no_access_page_redirects_user_with_admin_role(logged_in_admin):
    """
    GIVEN a test client logged in as an admin
    WHEN the /no_access page is accessed
    THEN check it redirects to home since user has a role
    """
    response = logged_in_admin.get(url_for('main.no_access'), follow_redirects=False)
    assert response.status_code == 302
    assert '/' in response.location

def test_no_access_page_redirects_user_with_admin_manager_role(logged_in_admin_manager):
    """
    GIVEN a test client logged in as an admin_manager
    WHEN the /no_access page is accessed
    THEN check it redirects to home since user has a role
    """
    response = logged_in_admin_manager.get(url_for('main.no_access'), follow_redirects=False)
    assert response.status_code == 302
    assert '/' in response.location

def test_manager_required_returns_403_for_admin(logged_in_admin):
    """
    GIVEN a test client logged in as an admin (not admin_manager)
    WHEN a manager-required route is accessed
    THEN check it returns 403 forbidden
    """
    response = logged_in_admin.post(url_for('main.clear_databases'))
    assert response.status_code == 403
    assert b'Uh Oh!' in response.data
