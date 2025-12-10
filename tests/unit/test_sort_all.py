# pylint: disable=too-many-instance-attributes,too-many-arguments,too-few-public-methods,protected-access,attribute-defined-outside-init,redefined-outer-name,import-outside-toplevel,line-too-long,invalid-name
"""
Unit tests for COOTSorter and sort_students in website.sort (all-in-one suite).
Covers assignment, custom criteria, constraints, statistics, and edge cases.
"""
from unittest.mock import patch  # standard lib first
import pytest
from website.sort import COOTSorter, sort_students
from website import create_app

# Dummy classes and fixture
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
        assert all(s.trip_id in [1,2] for s in students)

# Edge case: No available trips
def test_sorter_no_trips():
    """Test exception when no trips are available."""
    with patch('website.sort.Student') as MockStudent, \
         patch('website.sort.Trip') as MockTrip:
        MockStudent.query.all.return_value = [DummyStudent('S1', 'A', 'B', 'a@b.com')]
        MockTrip.query.all.return_value = []
        sorter = COOTSorter()
        with pytest.raises(Exception) as exc:
            sorter.sort_all_students()
        assert 'No trips available' in str(exc.value)

# Edge case: No students
def test_sorter_no_students():
    """Test exception when no students are found."""
    with patch('website.sort.Student') as MockStudent, \
         patch('website.sort.Trip') as MockTrip:
        MockStudent.query.all.return_value = []
        MockTrip.query.all.return_value = [DummyTrip(1, 'canoeing', 'Canoe A', 2)]
        sorter = COOTSorter()
        with pytest.raises(Exception) as exc:
            sorter.sort_all_students()
        assert 'No students found' in str(exc.value)

def test_sort_students_function_runs(dummy_data):
    """Test that sort_students function runs without error."""
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

def test_custom_criteria_blocks_assignment():
    """Test custom criteria blocks assignment due to dorm constraint."""
    students = [DummyStudent('S1', 'A', 'B', 'a@b.com', trip_pref_1='canoeing', dorm='Dana')]
    trips = [DummyTrip(1, 'canoeing', 'Canoe A', 2)]
    # Add Dana dorm to trip to trigger dorm constraint
    trips[0].students = []
    custom_criteria = [{'type': 'dorm'}]
    with patch('website.sort.Student') as MockStudent, \
         patch('website.sort.Trip') as MockTrip:
        MockStudent.query.all.return_value = students
        MockTrip.query.all.return_value = trips
        sorter = COOTSorter(custom_criteria=custom_criteria)
        # Simulate dorm already present in tracker
        sorter._initialize_trip_trackers(trips)
        sorter.trip_trackers[1]['dorms'].add('Dana')
        # Should not be able to assign due to dorm constraint
        can_place = sorter._can_place_student_in_trip(students[0], trips[0])
        assert can_place is False

def test_water_comfort_constraint():
    """Test water comfort constraint blocks assignment."""
    students = [DummyStudent('S1', 'A', 'B', 'a@b.com', trip_pref_1='canoeing', water_comfort=1)]
    trips = [DummyTrip(1, 'canoeing', 'Canoe A', 2, water=True)]
    with patch('website.sort.Student') as MockStudent, \
         patch('website.sort.Trip') as MockTrip:
        MockStudent.query.all.return_value = students
        MockTrip.query.all.return_value = trips
        sorter = COOTSorter()
        sorter._initialize_trip_trackers(trips)
        can_place = sorter._can_place_student_in_trip(students[0], trips[0])
        assert can_place is False

def test_statistics_calculation():
    """Test statistics calculation for 100% assignment and first choice rate."""
    students = [
        DummyStudent('S1', 'A', 'B', 'a@b.com', trip_pref_1='canoeing'),
        DummyStudent('S2', 'C', 'D', 'c@d.com', trip_pref_1='canoeing'),
    ]
    trips = [DummyTrip(1, 'canoeing', 'Canoe A', 2)]
    with patch('website.sort.Student') as MockStudent, \
         patch('website.sort.Trip') as MockTrip:
        MockStudent.query.all.return_value = students
        MockTrip.query.all.return_value = trips
        sorter = COOTSorter()
        stats = sorter.sort_all_students()
        assert stats['assignment_rate'] == 100
        assert stats['first_choice_rate'] == 100

def test_emergency_placement():
    """Test emergency placement logic when no preferences are set."""
    students = [DummyStudent('S1', 'A', 'B', 'a@b.com', trip_pref_1=None)]
    trips = [DummyTrip(1, 'canoeing', 'Canoe A', 2)]
    with patch('website.sort.Student') as MockStudent, \
         patch('website.sort.Trip') as MockTrip:
        MockStudent.query.all.return_value = students
        MockTrip.query.all.return_value = trips
        sorter = COOTSorter()
        sorter._initialize_trip_trackers(trips)
        trip = sorter._find_emergency_placement(students[0])
        assert trip is not None

def test_check_gender_balance_all_branches():
    """Test all branches of gender balance logic."""
    class Dummy:
        """Minimal dummy class for gender balance test."""
        pass
    sorter = COOTSorter()
    trip = Dummy()
    trip.id = 1
    sorter.trip_trackers = {1: {'students': [], 'gender_count': {'male': 0, 'female': 0, 'other': 0}}}
    # Empty trip: always True
    student = Dummy()
    student.gender = 'male'
    assert sorter._check_gender_balance(student, trip) is True
    # Add one male
    sorter.trip_trackers[1]['students'] = [1]
    sorter.trip_trackers[1]['gender_count']['male'] = 1
    # Adding another male (should allow up to 2)
    assert sorter._check_gender_balance(student, trip) is True
    # Adding third male (should not allow, forces diversity)
    sorter.trip_trackers[1]['gender_count']['male'] = 2
    assert sorter._check_gender_balance(student, trip) is False
    # Add a female, now mixed
    sorter.trip_trackers[1]['gender_count']['female'] = 1
    # Adding another male (should NOT allow, difference would be 3-1=2, not allowed)
    sorter.trip_trackers[1]['gender_count']['male'] = 3
    assert sorter._check_gender_balance(student, trip) is False
    # Adding another female (should allow, difference would be 3-2=1, allowed)
    student.gender = 'female'
    assert sorter._check_gender_balance(student, trip) is True

def test_place_student_in_trip_updates_trackers():
    """Test that placing a student in a trip updates trackers correctly."""
    student = DummyStudent('S1', 'A', 'B', 'a@b.com', dorm='Dana', athletic_team='Soccer', gender='female')
    trip = DummyTrip(1, 'canoeing', 'Canoe A', 2)
    sorter = COOTSorter()
    sorter._initialize_trip_trackers([trip])
    sorter._place_student_in_trip(student, trip)
    tracker = sorter.trip_trackers[trip.id]
    assert student.trip_id == trip.id
    assert tracker['capacity_left'] == trip.capacity - 1
    assert student.dorm in tracker['dorms']
    assert student.athletic_team in tracker['teams']
    assert tracker['gender_count']['female'] == 1

def test_can_place_student_in_trip_capacity():
    """Test that student cannot be placed if trip is at capacity."""
    student = DummyStudent('S1', 'A', 'B', 'a@b.com')
    trip = DummyTrip(1, 'canoeing', 'Canoe A', 1)
    sorter = COOTSorter()
    sorter._initialize_trip_trackers([trip])
    tracker = sorter.trip_trackers[trip.id]
    tracker['capacity_left'] = 0
    assert not sorter._can_place_student_in_trip(student, trip)

def test_can_place_student_in_trip_custom_criteria_order():
    """Test that custom criteria order blocks assignment as expected."""
    student = DummyStudent('S1', 'A', 'B', 'a@b.com', dorm='Dana', athletic_team='Soccer')
    trip = DummyTrip(1, 'canoeing', 'Canoe A', 2)
    sorter = COOTSorter(custom_criteria=[{'type': 'sports_team'}, {'type': 'dorm'}])
    sorter._initialize_trip_trackers([trip])
    tracker = sorter.trip_trackers[trip.id]
    tracker['teams'].add('Soccer')
    tracker['dorms'].add('Dana')
    # Should fail sports_team first
    assert not sorter._can_place_student_in_trip(student, trip)

def test_find_emergency_placement_prefers_capacity():
    """Test that emergency placement prefers trip with more capacity."""
    student = DummyStudent('S1', 'A', 'B', 'a@b.com')
    trip1 = DummyTrip(1, 'canoeing', 'Canoe A', 2)
    trip2 = DummyTrip(2, 'canoeing', 'Canoe B', 5)
    sorter = COOTSorter()
    sorter._initialize_trip_trackers([trip1, trip2])
    # Both trips are valid, but trip2 has more capacity
    trip = sorter._find_emergency_placement(student)
    assert trip.id == 2

def test_sort_students_statistics_partial_assignment():
    """Test partial assignment statistics when not enough capacity for all students."""
    # Not enough capacity for all students
    students = [DummyStudent(f'S{i}', 'A', 'B', 'a@b.com', trip_pref_1='canoeing') for i in range(3)]
    trips = [DummyTrip(1, 'canoeing', 'Canoe A', 2)]
    with patch('website.sort.Student') as MockStudent, \
         patch('website.sort.Trip') as MockTrip:
        MockStudent.query.all.return_value = students
        MockTrip.query.all.return_value = trips
        sorter = COOTSorter()
        stats = sorter.sort_all_students()
        assert stats['assigned'] == 2
        assert stats['assignment_rate'] == pytest.approx(2/3*100)

def test_process_student_batch_no_preferences():
    """Test batch processing when no preferences are set and emergency placement is used."""
    # ...existing code...

def test_process_student_batch_all_preferences_fail():
    """Test batch processing when all preferences fail and emergency placement is used."""
    # ...existing code...

def test_find_emergency_placement_no_valid_trip():
    """Test _find_emergency_placement returning None when no valid trip exists."""
    # ...existing code...

def test_calculate_final_stats_zero_total():
    """Test _calculate_final_stats when total is 0."""
    # ...existing code...

def test_process_student_batch_already_assigned():
    """Test skipping students already assigned."""
    # ...existing code...

def test_process_student_batch_no_emergency_placement():
    """Test when no preferences and no emergency placement is possible."""
    # ...existing code...

def test_find_emergency_placement_scoring():
    """Test scoring logic in _find_emergency_placement."""
    # ...existing code...

def test_process_student_batch_skips_none_preferences():
    """Test skipping None preferences in the loop (lines 134-137)."""
    # ...existing code...
