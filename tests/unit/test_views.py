""" This file contains unit tests for the website.views file.

This includes tests for the validate_trip function.
"""

from website.views import validate_trip

class DummyStudent:
    """Create a dummy student object for testing purposes."""
    def __init__(
        self,
        first_name="Test",
        last_name="Student",
        gender=None,
        dorm=None,
        athletic_team=None,
        water_comfort=None,
        tent_comfort=None,
    ):
        self.first_name = first_name
        self.last_name = last_name
        self.gender = gender
        self.dorm = dorm
        self.athletic_team = athletic_team
        self.water_comfort = water_comfort
        self.tent_comfort = tent_comfort

class DummyTrip:
    """Create a dummy trip object for testing purposes."""
    def __init__(self, students=None, water=False, tent=False):
        self.students = students or []
        self.water = water
        self.tent = tent

def test_validate_trip_empty_students():
    """
    GIVEN a trip with no students
    WHEN validate_trip is called
    THEN check all validations pass
    """
    trip = DummyTrip(students=[])
    validations = validate_trip(trip)

    assert validations["overall_valid"] is True
    assert validations["gender_ratio"]["valid"] is True
    assert validations["athletic_teams"]["valid"] is True
    assert validations["roommates"]["valid"] is True
    assert validations["comfort_levels"]["valid"] is True

def test_validate_trip_gender_balance_valid():
    """
    GIVEN a trip with balanced gender distribution
    WHEN validate_trip is called
    THEN check gender validation passes
    """
    students = [
        DummyStudent(first_name="Male", last_name="One", gender="Male"),
        DummyStudent(first_name="Female", last_name="One", gender="Female"),
    ]
    trip = DummyTrip(students=students)

    validations = validate_trip(trip)

    assert validations["gender_ratio"]["valid"] is True
    assert validations["overall_valid"] is True
    assert "1 Male" in validations["gender_ratio"]["message"]
    assert "1 Female" in validations["gender_ratio"]["message"]

def test_validate_trip_gender_imbalance():
    """
    GIVEN a trip with imbalanced gender distribution
    WHEN validate_trip is called
    THEN check gender validation fails
    """
    students = [
        DummyStudent(first_name="Male", last_name="One", gender="Male"),
        DummyStudent(first_name="Male", last_name="Two", gender="Male"),
        DummyStudent(first_name="Male", last_name="Three", gender="Male"),
        DummyStudent(first_name="Female", last_name="One", gender="Female"),
    ]
    trip = DummyTrip(students=students)

    validations = validate_trip(trip)

    assert validations["gender_ratio"]["valid"] is False
    assert validations["overall_valid"] is False
    # 3 vs 1 → diff = 2
    assert "3 Male" in validations["gender_ratio"]["message"]
    assert "1 Female" in validations["gender_ratio"]["message"]
    assert "off by 2" in validations["gender_ratio"]["details"]

def test_validate_trip_duplicate_athletic_teams():
    """
    GIVEN a trip with students from the same athletic team
    WHEN validate_trip is called
    THEN check athletic team validation fails
    """
    students = [
        DummyStudent(
            first_name="Player",
            last_name="One",
            athletic_team="Soccer",
        ),
        DummyStudent(
            first_name="Player",
            last_name="Two",
            athletic_team="Soccer",
        ),
    ]
    trip = DummyTrip(students=students)

    validations = validate_trip(trip)

    assert validations["athletic_teams"]["valid"] is False
    assert validations["overall_valid"] is False
    assert any("Soccer" in detail for detail in validations["athletic_teams"]["details"])
    assert "Player One" in validations["athletic_teams"]["details"][0]
    assert "Player Two" in validations["athletic_teams"]["details"][0]

def test_validate_trip_duplicate_dorms():
    """
    GIVEN a trip with students from the same dorm
    WHEN validate_trip is called
    THEN check dorm validation fails
    """
    students = [
        DummyStudent(
            first_name="Roommate",
            last_name="One",
            dorm="Dana",
        ),
        DummyStudent(
            first_name="Roommate",
            last_name="Two",
            dorm="Dana",
        ),
    ]
    trip = DummyTrip(students=students)

    validations = validate_trip(trip)

    assert validations["roommates"]["valid"] is False
    assert validations["overall_valid"] is False
    assert any("Dana" in detail for detail in validations["roommates"]["details"])
    assert "Roommate One" in validations["roommates"]["details"][0]
    assert "Roommate Two" in validations["roommates"]["details"][0]

def test_validate_trip_low_water_comfort():
    """
    GIVEN a water trip with students having low water comfort
    WHEN validate_trip is called
    THEN check comfort level validation fails
    """
    students = [
        DummyStudent(
            first_name="Low",
            last_name="Comfort",
            water_comfort=1,
        )
    ]
    trip = DummyTrip(students=students, water=True, tent=False)

    validations = validate_trip(trip)

    assert validations["comfort_levels"]["valid"] is False
    assert validations["overall_valid"] is False
    assert any("Low water comfort" in d for d in validations["comfort_levels"]["details"])
    assert "Low Comfort" in validations["comfort_levels"]["details"][0]

def test_validate_trip_low_tent_comfort():
    """
    GIVEN a tent trip with students having low tent comfort
    WHEN validate_trip is called
    THEN check comfort level validation fails
    """
    students = [
        DummyStudent(
            first_name="Low",
            last_name="Comfort",
            tent_comfort=2,
        )
    ]
    trip = DummyTrip(students=students, water=False, tent=True)

    validations = validate_trip(trip)

    assert validations["comfort_levels"]["valid"] is False
    assert validations["overall_valid"] is False
    assert any("Low tent comfort" in d for d in validations["comfort_levels"]["details"])
    assert "Low Comfort" in validations["comfort_levels"]["details"][0]

def test_validate_trip_all_validations_pass():
    """
    GIVEN a trip with all validations passing
    WHEN validate_trip is called
    THEN check all validations pass
    """
    students = [
        DummyStudent(
            first_name="Valid",
            last_name="One",
            gender="Male",
            dorm="Dana",
            athletic_team="Soccer",
            water_comfort=4,
            tent_comfort=4,
        ),
        DummyStudent(
            first_name="Valid",
            last_name="Two",
            gender="Female",
            dorm="West",
            athletic_team="Basketball",
            water_comfort=4,
            tent_comfort=4,
        ),
    ]
    trip = DummyTrip(students=students, water=False, tent=False)

    validations = validate_trip(trip)

    assert validations["overall_valid"] is True
    assert validations["gender_ratio"]["valid"] is True
    assert validations["athletic_teams"]["valid"] is True
    assert validations["roommates"]["valid"] is True
    assert validations["comfort_levels"]["valid"] is True

def test_validate_trip_athletic_team_none_values():
    """
    GIVEN a trip with students having None or 'N/A' athletic teams
    WHEN validate_trip is called
    THEN check athletic team validation passes (None/N/A teams are ignored)
    """
    students = [
        DummyStudent(
            first_name="No",
            last_name="Team",
            athletic_team=None,
        ),
        DummyStudent(
            first_name="N/A",
            last_name="Team",
            athletic_team="N/A",
        ),
    ]
    trip = DummyTrip(students=students)

    validations = validate_trip(trip)

    # No duplicates among "real" athletic teams
    assert validations["athletic_teams"]["valid"] is True
    assert validations["overall_valid"] is True

def test_validate_trip_gender_none_values():
    """
    GIVEN a trip with students having None gender values
    WHEN validate_trip is called
    THEN check gender validation handles None values correctly
    """
    students = [
        DummyStudent(
            first_name="No",
            last_name="Gender",
            gender=None,
        ),
        DummyStudent(
            first_name="Male",
            last_name="One",
            gender="Male",
        ),
    ]
    trip = DummyTrip(students=students)

    validations = validate_trip(trip)

    # Still returns gender_ratio key and should be valid (1 vs 0 diff <= 1)
    assert "gender_ratio" in validations
    assert validations["gender_ratio"]["valid"] is True
    assert validations["overall_valid"] is True

def test_validate_trip_water_comfort_none():
    """
    GIVEN a water trip with students having None water_comfort
    WHEN validate_trip is called
    THEN check comfort validation handles None values correctly
    """
    students = [
        DummyStudent(
            first_name="No",
            last_name="Comfort",
            water_comfort=None,
        )
    ]
    trip = DummyTrip(students=students, water=True, tent=False)

    validations = validate_trip(trip)

    # None water comfort should NOT trigger low comfort
    assert validations["comfort_levels"]["valid"] is True
    assert validations["overall_valid"] is True

def test_validate_trip_high_water_comfort():
    """
    GIVEN a water trip with students having high water comfort
    WHEN validate_trip is called
    THEN check comfort validation passes
    """
    students = [
        DummyStudent(
            first_name="High",
            last_name="Comfort",
            water_comfort=5,
        )
    ]
    trip = DummyTrip(students=students, water=True, tent=False)

    validations = validate_trip(trip)

    assert validations["comfort_levels"]["valid"] is True
    assert validations["overall_valid"] is True
