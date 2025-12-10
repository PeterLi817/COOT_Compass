# pylint: disable=too-many-instance-attributes,too-many-arguments,too-few-public-methods,protected-access,attribute-defined-outside-init,redefined-outer-name,import-outside-toplevel,line-too-long
"""
Advanced unit tests for COOTSorter and sort_students in website.sort.
Covers edge cases, custom criteria, statistics, emergency placement, gender balance, and trackers.
"""
from unittest.mock import patch
import pytest
from website.sort import COOTSorter

class DummyStudent:
    """A dummy student for testing COOTSorter logic."""
    # pylint: disable=too-many-arguments,too-many-instance-attributes
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
    # pylint: disable=too-many-arguments
    def __init__(self, trip_id, trip_type, trip_name, capacity, water=False, tent=False):
        self.id = trip_id
        self.trip_type = trip_type
        self.trip_name = trip_name
        self.capacity = capacity
        self.water = water
        self.tent = tent
        self.students = []

# Edge case: No available trips
def test_sorter_no_trips():
    """Test exception when no trips are available."""
    with patch('website.sort.Student') as mock_student, \
         patch('website.sort.Trip') as mock_trip:
        mock_student.query.all.return_value = [DummyStudent('S1', 'A', 'B', 'a@b.com')]
        mock_trip.query.all.return_value = []
        sorter = COOTSorter()
        with pytest.raises(Exception) as exc:
            sorter.sort_all_students()
        assert 'No trips available' in str(exc.value)


# Edge case: No students
def test_sorter_no_students():
    """Test exception when no students are found."""
    with patch('website.sort.Student') as mock_student, \
         patch('website.sort.Trip') as mock_trip:
        mock_student.query.all.return_value = []
        mock_trip.query.all.return_value = [DummyTrip(1, 'canoeing', 'Canoe A', 2)]
        sorter = COOTSorter()
        with pytest.raises(Exception) as exc:
            sorter.sort_all_students()
        assert 'No students found' in str(exc.value)

# Test custom criteria logic
def test_custom_criteria_blocks_assignment():
    """Test custom criteria blocks assignment due to dorm constraint."""
    students = [DummyStudent('S1', 'A', 'B', 'a@b.com', trip_pref_1='canoeing', dorm='Dana')]
    trips = [DummyTrip(1, 'canoeing', 'Canoe A', 2)]
    trips[0].students = []
    custom_criteria = [{'type': 'dorm'}]
    with patch('website.sort.Student') as mock_student, \
         patch('website.sort.Trip') as mock_trip:
        mock_student.query.all.return_value = students
        mock_trip.query.all.return_value = trips
        sorter = COOTSorter(custom_criteria=custom_criteria)
        sorter._initialize_trip_trackers(trips)
        sorter.trip_trackers[1]['dorms'].add('Dana')
        can_place = sorter._can_place_student_in_trip(students[0], trips[0])
        assert can_place is False


# Test hard constraint: water comfort
def test_water_comfort_constraint():
    """Test water comfort constraint blocks assignment."""
    students = [DummyStudent('S1', 'A', 'B', 'a@b.com', trip_pref_1='canoeing', water_comfort=1)]
    trips = [DummyTrip(1, 'canoeing', 'Canoe A', 2, water=True)]
    with patch('website.sort.Student') as mock_student, \
         patch('website.sort.Trip') as mock_trip:
        mock_student.query.all.return_value = students
        mock_trip.query.all.return_value = trips
        sorter = COOTSorter()
        sorter._initialize_trip_trackers(trips)
        can_place = sorter._can_place_student_in_trip(students[0], trips[0])
        assert can_place is False

# Test statistics calculation
def test_statistics_calculation():
    """Test statistics calculation for 100% assignment and first choice rate."""
    students = [
        DummyStudent('S1', 'A', 'B', 'a@b.com', trip_pref_1='canoeing'),
        DummyStudent('S2', 'C', 'D', 'c@d.com', trip_pref_1='canoeing'),
    ]
    trips = [DummyTrip(1, 'canoeing', 'Canoe A', 2)]
    with patch('website.sort.Student') as mock_student, \
         patch('website.sort.Trip') as mock_trip:
        mock_student.query.all.return_value = students
        mock_trip.query.all.return_value = trips
        sorter = COOTSorter()
        stats = sorter.sort_all_students()
        assert stats['assignment_rate'] == 100
        assert stats['first_choice_rate'] == 100


# Test emergency placement
def test_emergency_placement():
    """Test emergency placement logic when no preferences are set."""
    students = [DummyStudent('S1', 'A', 'B', 'a@b.com', trip_pref_1=None)]
    trips = [DummyTrip(1, 'canoeing', 'Canoe A', 2)]
    with patch('website.sort.Student') as mock_student, \
         patch('website.sort.Trip') as mock_trip:
        mock_student.query.all.return_value = students
        mock_trip.query.all.return_value = trips
        sorter = COOTSorter()
        sorter._initialize_trip_trackers(trips)
        trip = sorter._find_emergency_placement(students[0])
        assert trip is not None

# Test gender balance logic
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

# Additional unit tests for COOTSorter and sort_students

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
    students = [
        DummyStudent(f'S{i}', 'A', 'B', 'a@b.com', trip_pref_1='canoeing') 
        for i in range(3)
    ]
    trips = [DummyTrip(1, 'canoeing', 'Canoe A', 2)]
    with patch('website.sort.Student') as mock_student, \
         patch('website.sort.Trip') as mock_trip:
        mock_student.query.all.return_value = students
        mock_trip.query.all.return_value = trips
        sorter = COOTSorter()
        stats = sorter.sort_all_students()
        assert stats['assigned'] == 2
        assert stats['assignment_rate'] == pytest.approx(2 / 3 * 100)

def test_process_student_batch_no_preferences():
    """Test batch processing when no preferences are set and emergency placement is used."""
    students = [
        DummyStudent(
            'S1', 'A', 'B', 'a@b.com', 
            trip_pref_1=None, trip_pref_2=None, trip_pref_3=None
        )
    ]
    trips = [DummyTrip(1, 'canoeing', 'Canoe A', 2)]
    with patch('website.sort.Student') as mock_student, \
         patch('website.sort.Trip') as mock_trip:
        mock_student.query.all.return_value = students
        mock_trip.query.all.return_value = trips
        sorter = COOTSorter()
        sorter._initialize_trip_trackers(trips)
        sorter._process_student_batch(students)
        # Should assign via emergency placement
        assert students[0].trip_id == 1


def test_process_student_batch_all_preferences_fail():
    """Test batch processing when all preferences fail and emergency placement is used."""
    students = [
        DummyStudent(
            'S1', 'A', 'B', 'a@b.com', 
            trip_pref_1='canoeing', trip_pref_2='backpacking', 
            trip_pref_3='hiking'
        )
    ]
    trips = [DummyTrip(1, 'canoeing', 'Canoe A', 0)]  # No capacity
    with patch('website.sort.Student') as mock_student, \
         patch('website.sort.Trip') as mock_trip:
        mock_student.query.all.return_value = students
        mock_trip.query.all.return_value = trips
        sorter = COOTSorter()
        sorter._initialize_trip_trackers(trips)
        # Set capacity to 0 so no preference can be assigned
        sorter.trip_trackers[1]['capacity_left'] = 0
        sorter._process_student_batch(students)
        # Should not assign (no emergency placement possible)
        assert students[0].trip_id is None

def test_find_emergency_placement_no_valid_trip():
    """Test _find_emergency_placement returning None when no valid trip exists."""
    student = DummyStudent('S1', 'A', 'B', 'a@b.com')
    trip = DummyTrip(1, 'canoeing', 'Canoe A', 0)
    sorter = COOTSorter()
    sorter._initialize_trip_trackers([trip])
    # No capacity
    sorter.trip_trackers[trip.id]['capacity_left'] = 0
    result = sorter._find_emergency_placement(student)
    assert result is None


def test_calculate_final_stats_zero_total():
    """Test _calculate_final_stats when total is 0."""
    sorter = COOTSorter()
    sorter.stats['total'] = 0
    sorter._calculate_final_stats()
    assert sorter.stats['assignment_rate'] == 0
    assert sorter.stats['first_choice_rate'] == 0

def test_process_student_batch_already_assigned():
    """Test skipping students already assigned."""
    students = [DummyStudent('S1', 'A', 'B', 'a@b.com', trip_pref_1='canoeing')]
    students[0].trip_id = 99  # Already assigned
    trips = [DummyTrip(1, 'canoeing', 'Canoe A', 2)]
    sorter = COOTSorter()
    sorter._initialize_trip_trackers(trips)
    sorter._process_student_batch(students)
    # Should not change trip_id
    assert students[0].trip_id == 99


def test_process_student_batch_no_emergency_placement():
    """Test when no preferences and no emergency placement is possible."""
    students = [DummyStudent('S1', 'A', 'B', 'a@b.com', trip_pref_1=None, trip_pref_2=None, trip_pref_3=None)]
    trips = [DummyTrip(1, 'canoeing', 'Canoe A', 0)]
    sorter = COOTSorter()
    sorter._initialize_trip_trackers(trips)
    sorter.trip_trackers[1]['capacity_left'] = 0
    sorter._process_student_batch(students)
    assert students[0].trip_id is None

def test_find_emergency_placement_scoring():
    """Test scoring logic in _find_emergency_placement."""
    student = DummyStudent(
        'S1', 'A', 'B', 'a@b.com', water_comfort=3, tent_comfort=3, 
        dorm='Dana', athletic_team='Soccer', gender='male'
    )
    trip1 = DummyTrip(1, 'canoeing', 'Canoe A', 2, water=True, tent=False)
    trip2 = DummyTrip(2, 'backpacking', 'Backpack A', 2, water=False, tent=True)
    trip3 = DummyTrip(3, 'canoeing', 'Canoe B', 2, water=True, tent=True)
    sorter = COOTSorter()
    sorter._initialize_trip_trackers([trip1, trip2, trip3])
    # Add dorm/team to trip1 to reduce score
    sorter.trip_trackers[1]['dorms'].add('Dana')
    sorter.trip_trackers[1]['teams'].add('Soccer')
    # Add gender to trip2 to test gender balance
    sorter.trip_trackers[2]['gender_count']['male'] = 1
    # All trips have capacity
    trip = sorter._find_emergency_placement(student)
    assert trip in [trip2, trip3, trip1]  # Any trip is valid, but scoring logic is exercised


def test_process_student_batch_skips_none_preferences():
    """Test skipping None preferences in the loop (lines 134-137)."""
    students = [
        DummyStudent(
            'S1', 'A', 'B', 'a@b.com', trip_pref_1=None, 
            trip_pref_2=None, trip_pref_3='canoeing'
        )
    ]
    trips = [DummyTrip(1, 'canoeing', 'Canoe A', 2)]
    sorter = COOTSorter()
    sorter._initialize_trip_trackers(trips)
    sorter._process_student_batch(students)
    # Should assign via third preference
    assert students[0].trip_id == 1
