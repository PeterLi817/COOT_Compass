"""
Unit tests for COOTSorter and sort_students in website.sort (basic unit tests).
Covers assignment, function execution, and dummy data setup.
"""
# pylint: disable=line-too-long,too-many-arguments,too-many-instance-attributes,too-few-public-methods,invalid-name,redefined-outer-name
from unittest.mock import patch  # standard lib first
import pytest
from website.sort import COOTSorter, sort_students
from website import create_app

class DummyStudent:
    """A dummy student for testing COOTSorter logic."""
    def __init__(self, student_id, first_name, last_name, email, trip_pref_1=None, trip_pref_2=None, trip_pref_3=None, dorm=None, athletic_team=None, gender=None, water_comfort=3, tent_comfort=3):
        self.id = student_id
        self.student_id = student_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.trip_pref_1 = trip_pref_1
        self.trip_pref_2 = trip_pref_2
        self.trip_pref_3 = trip_pref_3
        self.dorm = dorm
        self.athletic_team = athletic_team
        self.gender = gender
        self.water_comfort = water_comfort
        self.tent_comfort = tent_comfort
        self.trip_id = None

class DummyTrip:
    """A dummy trip for testing COOTSorter logic."""
    def __init__(self, trip_id, trip_type, trip_name, capacity, water=False, tent=False):
        self.id = trip_id
        self.trip_type = trip_type
        self.trip_name = trip_name
        self.capacity = capacity
        self.water = water
        self.tent = tent
        self.students = []

@pytest.fixture
def dummy_data():
    """Fixture providing dummy students and trips for tests."""
    trips = [
        DummyTrip(1, 'canoeing', 'Canoe A', 2, water=True),
        DummyTrip(2, 'backpacking', 'Backpack A', 2, tent=True),
    ]
    students = [
        DummyStudent('S1', 'Alice', 'Smith', 'alice@example.com', trip_pref_1='canoeing', gender='female', water_comfort=3),
        DummyStudent('S2', 'Bob', 'Jones', 'bob@example.com', trip_pref_1='backpacking', gender='male', tent_comfort=3),
        DummyStudent('S3', 'Charlie', 'Brown', 'charlie@example.com', trip_pref_1='canoeing', gender='male', water_comfort=3),
    ]
    return students, trips

def test_sorter_assigns_students_to_trips(dummy_data):
    """Test that students are assigned to trips as expected."""
    students, trips = dummy_data
    with patch('website.sort.Student') as MockStudent, \
         patch('website.sort.Trip') as MockTrip:
        MockStudent.query.all.return_value = students
        MockTrip.query.all.return_value = trips
        sorter = COOTSorter()
        stats = sorter.sort_all_students()
        assigned = [s for s in students if s.trip_id is not None]
        assert stats['assigned'] == len(assigned)
        assert stats['assigned'] == 3
        assert all(s.trip_id in [1, 2] for s in students)

def test_sort_students_function_runs(dummy_data):
    """Test that sort_students function runs without error and assigns all students."""
    students, trips = dummy_data
    app = create_app()
    with app.app_context():
        with patch('website.sort.Student') as MockStudent, \
             patch('website.sort.Trip') as MockTrip, \
             patch('website.views.validate_trip', return_value={'overall_valid': True}), \
             patch('website.sort.db.session.expire', return_value=None):
            MockStudent.query.all.return_value = students
            MockTrip.query.all.return_value = trips
            stats = sort_students()
            assert stats['all_valid'] is True
            assert stats['assigned'] == 3
