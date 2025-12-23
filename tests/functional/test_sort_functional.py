"""
Functional tests for the COOT sorting algorithm with database integration.
Tests the sort_students() function that interacts with the database.
"""
# pylint: disable=missing-function-docstring,invalid-name,unused-argument
import pytest
from website import db
from website.models import Student, Trip
from website.sort import sort_students, COOTSorter


def test_sort_students_no_students_exception(app):
    """Test that sort_students raises exception when no students exist."""
    with app.app_context():
        # Ensure database is empty
        Student.query.delete()
        Trip.query.delete()
        db.session.commit()

        # Add a trip but no students
        trip = Trip(trip_name='Test Trip', trip_type='hiking', capacity=10)
        db.session.add(trip)
        db.session.commit()

        # Should raise exception
        sorter = COOTSorter()
        with pytest.raises(Exception, match="No students found to sort"):
            sorter.sort_all_students()


def test_sort_students_no_trips_exception(app):
    """Test that sort_students raises exception when no trips exist."""
    with app.app_context():
        # Ensure database is empty
        Student.query.delete()
        Trip.query.delete()
        db.session.commit()

        # Add a student but no trips
        student = Student(
            student_id='S1',
            first_name='Test',
            last_name='Student',
            email='test@colby.edu',
            gender='male',
            dorm='Dana'
        )
        db.session.add(student)
        db.session.commit()

        # Should raise exception
        sorter = COOTSorter()
        with pytest.raises(Exception, match="No trips available for sorting"):
            sorter.sort_all_students()


# def test_sort_students_with_custom_criteria_prints_debug(app, capsys):
#     """Test that custom criteria triggers print statements."""
#     with app.app_context():
#         # Clear database
#         Student.query.delete()
#         Trip.query.delete()
#         db.session.commit()

#         # Add a trip
#         trip = Trip(trip_name='Test Trip', trip_type='hiking', capacity=10)
#         db.session.add(trip)

#         # Add a student with matching preference
#         student = Student(
#             student_id='S1',
#             first_name='Test',
#             last_name='Student',
#             email='test@colby.edu',
#             gender='male',
#             dorm='Dana',
#             trip_pref_1='hiking'
#         )
#         db.session.add(student)
#         db.session.commit()

#         # Run sort with custom criteria to trigger print statements
#         sorter = COOTSorter(custom_criteria=[{'type': 'dorm'}, {'type': 'gender'}])
#         sorter.sort_all_students()

#         # Check that debug print was called (lines 281, 285, 289, 291)
#         captured = capsys.readouterr()
#         assert 'custom criteria order' in captured.out or 'Checking' in captured.out


def test_sort_students_emergency_placement_scoring(app):
    """Test emergency placement scoring logic for water and tent comfort."""
    with app.app_context():
        # Clear database
        Student.query.delete()
        Trip.query.delete()
        db.session.commit()

        # Add trips with different features
        trip1 = Trip(trip_name='Water Trip', trip_type='canoeing', capacity=10, water=True, tent=False)
        trip2 = Trip(trip_name='Tent Trip', trip_type='camping', capacity=10, water=False, tent=True)
        trip3 = Trip(trip_name='Regular Trip', trip_type='hiking', capacity=10, water=False, tent=False)
        db.session.add_all([trip1, trip2, trip3])

        # Add student with low water comfort, no preferences match
        student = Student(
            student_id='S1',
            first_name='Test',
            last_name='Student',
            email='test@colby.edu',
            gender='male',
            dorm='Dana',
            water_comfort=1,  # Low water comfort
            tent_comfort=5,
            trip_pref_1='biking',  # No such trip type
            trip_pref_2='running',
            trip_pref_3='swimming'
        )
        db.session.add(student)
        db.session.commit()

        # Run sort - should use emergency placement and avoid water trip
        sorter = COOTSorter()
        stats = sorter.sort_all_students()

        # Student should be assigned via emergency placement
        assert student.trip_id is not None
        # Should not be assigned to water trip (trip1)
        assert student.trip_id != trip1.id


def test_sort_students_validation_loop(app):
    """Test that sort_students loops when validation fails."""
    with app.app_context():
        # Clear database
        Student.query.delete()
        Trip.query.delete()
        db.session.commit()

        # Add a trip with limited capacity
        trip = Trip(trip_name='Test Trip', trip_type='hiking', capacity=5)
        db.session.add(trip)

        # Add students with preferences
        for i in range(3):
            student = Student(
                student_id=f'S{i}',
                first_name='Test',
                last_name=f'Student{i}',
                email=f'test{i}@colby.edu',
                gender='male' if i % 2 == 0 else 'female',
                dorm=f'Dorm{i}',
                trip_pref_1='hiking'
            )
            db.session.add(student)
        db.session.commit()

        # Run sort - may attempt multiple times to satisfy validation
        stats = sort_students()

        # Check that attempts key exists (from lines 518-528)
        assert 'attempts' in stats
        assert stats['attempts'] >= 1


def test_sort_students_max_attempts_reached(app, monkeypatch):
    """Test that sort_students handles max attempts."""
    with app.app_context():
        # Clear database
        Student.query.delete()
        Trip.query.delete()
        db.session.commit()

        # Add a trip
        trip = Trip(trip_name='Test Trip', trip_type='hiking', capacity=10)
        db.session.add(trip)

        # Add students
        for i in range(2):
            student = Student(
                student_id=f'S{i}',
                first_name='Test',
                last_name=f'Student{i}',
                email=f'test{i}@colby.edu',
                gender='male',
                dorm='Dana',  # Same dorm - will trigger validation failure
                trip_pref_1='hiking'
            )
            db.session.add(student)
        db.session.commit()

        # Mock validate_trip to always return invalid
        from website import views
        original_validate = views.validate_trip
        def mock_validate(trip):
            return {
                'overall_valid': False,
                'gender_balance': {'valid': False, 'warning': 'Test failure'},
                'duplicate_athletic_teams': {'valid': True, 'warning': None},
                'duplicate_dorms': {'valid': True, 'warning': None},
                'water_comfort': {'valid': True, 'warning': None},
                'tent_comfort': {'valid': True, 'warning': None}
            }
        monkeypatch.setattr(views, 'validate_trip', mock_validate)

        # Run sort - should hit max attempts
        stats = sort_students()

        # Should return with all_valid False
        assert 'all_valid' in stats
        assert stats['attempts'] == 100  # Max attempts


def test_categorize_students_with_water_trip(app):
    """Test _categorize_students when water trips exist and student has low water comfort."""
    with app.app_context():
        # Clear database
        Student.query.delete()
        Trip.query.delete()
        db.session.commit()

        # Add a water trip
        trip = Trip(trip_name='Water Trip', trip_type='canoeing', capacity=10, water=True)
        db.session.add(trip)

        # Add student with low water comfort
        student = Student(
            student_id='S1',
            first_name='Test',
            last_name='Student',
            email='test@colby.edu',
            gender='male',
            dorm='Dana',
            water_comfort=2,  # Low comfort
            tent_comfort=5,
            trip_pref_1='canoeing'
        )
        db.session.add(student)
        db.session.commit()

        sorter = COOTSorter()
        students = Student.query.all()
        trips = Trip.query.all()

        priority, regular = sorter._categorize_students(students, trips)

        # Student with low water comfort should be in priority
        assert len(priority) == 1
        assert len(regular) == 0


def test_categorize_students_with_tent_trip(app):
    """Test _categorize_students when tent trips exist and student has low tent comfort."""
    with app.app_context():
        # Clear database
        Student.query.delete()
        Trip.query.delete()
        db.session.commit()

        # Add a tent trip
        trip = Trip(trip_name='Tent Trip', trip_type='camping', capacity=10, tent=True)
        db.session.add(trip)

        # Add student with low tent comfort
        student = Student(
            student_id='S1',
            first_name='Test',
            last_name='Student',
            email='test@colby.edu',
            gender='male',
            dorm='Dana',
            water_comfort=5,
            tent_comfort=1,  # Low comfort
            trip_pref_1='camping'
        )
        db.session.add(student)
        db.session.commit()

        sorter = COOTSorter()
        students = Student.query.all()
        trips = Trip.query.all()

        priority, regular = sorter._categorize_students(students, trips)

        # Student with low tent comfort should be in priority
        assert len(priority) == 1
        assert len(regular) == 0
