"""
Unit tests for COOTSorter._categorize_students covering edge cases and rare branches
(no constraints, all constraints, mixed).
"""
# pylint: disable=line-too-long,protected-access
from website.sort import COOTSorter

class DummyStudent:
    """Dummy student for testing categorization logic."""
    # pylint: disable=too-many-arguments,too-many-instance-attributes,too-few-public-methods
    def __init__(self, student_id, water_comfort=3, tent_comfort=3):
        self.id = student_id
        self.student_id = student_id
        self.water_comfort = water_comfort
        self.tent_comfort = tent_comfort

class DummyTrip:
    """Dummy trip for testing categorization logic."""
    # pylint: disable=too-many-arguments,too-few-public-methods
    def __init__(self, trip_id, water=False, tent=False):
        self.id = trip_id
        self.water = water
        self.tent = tent


def test_categorize_students_all_priority():
    """All students should be categorized as priority if they have low comfort and trips require it."""
    students = [
        DummyStudent('S1', water_comfort=1),
        DummyStudent('S2', tent_comfort=1)
    ]
    trips = [DummyTrip(1, water=True, tent=True)]
    sorter = COOTSorter()
    priority, regular = sorter._categorize_students(students, trips)
    assert len(priority) == 2
    assert len(regular) == 0


def test_categorize_students_all_regular():
    """All students should be categorized as regular if they have high comfort."""
    students = [
        DummyStudent('S1', water_comfort=3, tent_comfort=3),
        DummyStudent('S2', water_comfort=4, tent_comfort=4)
    ]
    trips = [DummyTrip(1, water=True, tent=True)]
    sorter = COOTSorter()
    priority, regular = sorter._categorize_students(students, trips)
    assert len(priority) == 0
    assert len(regular) == 2


def test_categorize_students_mixed():
    """Mixed comfort students: some should be priority, some regular."""
    students = [
        DummyStudent('S1', water_comfort=1, tent_comfort=3),
        DummyStudent('S2', water_comfort=3, tent_comfort=1),
        DummyStudent('S3', water_comfort=3, tent_comfort=3)
    ]
    trips = [DummyTrip(1, water=True, tent=True)]
    sorter = COOTSorter()
    priority, regular = sorter._categorize_students(students, trips)
    assert len(priority) == 2
    assert len(regular) == 1


def test_categorize_students_no_trips():
    """If there are no trips, all students should be regular (no constraints triggered)."""
    students = [DummyStudent('S1', water_comfort=1, tent_comfort=1)]
    trips = []
    sorter = COOTSorter()
    priority, regular = sorter._categorize_students(students, trips)
    assert len(priority) == 0
    assert len(regular) == 1
