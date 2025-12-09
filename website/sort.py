"""Student sorting algorithm for COOT trip assignments.

This module implements an intelligent sorting algorithm that assigns students
to trips based on their preferences while respecting various constraints
including capacity, gender balance, dorm assignments, athletic teams, and
comfort levels. The algorithm prioritizes students with special constraints
and attempts to maximize preference satisfaction.
"""

import random
from collections import defaultdict
from website import db
from .models import Student, Trip

class COOTSorter:
    """Intelligent COOT student sorting algorithm.

    This class implements a sophisticated sorting algorithm that assigns
    students to trips while balancing multiple constraints and preferences.
    It tracks statistics about the sorting process and can use custom
    criteria ordering for constraint checking.
    """

    def __init__(self, custom_criteria=None):
        """Initialize the COOT sorter with optional custom criteria.

        Args:
            custom_criteria (list, optional): List of criteria dictionaries
                specifying custom constraint checking order. Each dictionary
                should have a 'type' key indicating the constraint type.
        """
        self.custom_criteria = custom_criteria or []
        self.trip_trackers = {}
        self.trips_by_type = defaultdict(list)
        self.stats = {
            'total': 0,
            'assigned': 0,
            'first_choice': 0,
            'second_choice': 0,
            'third_choice': 0,
            'no_preference': 0,
            'assignment_rate': 0,
            'first_choice_rate': 0
        }

    def sort_all_students(self):
        """Main sorting function that assigns all students to trips.

        Processes all students and assigns them to trips based on their
        preferences while respecting constraints. Students with special
        constraints (low water/tent comfort) are processed first. The
        algorithm attempts to satisfy preferences in order (first, second,
        third) and uses emergency placement for students whose preferences
        cannot be satisfied.

        Returns:
            dict: Statistics dictionary containing:
                - total: Total number of students
                - assigned: Number of students successfully assigned
                - first_choice: Number assigned to first preference
                - second_choice: Number assigned to second preference
                - third_choice: Number assigned to third preference
                - no_preference: Number assigned via emergency placement
                - assignment_rate: Percentage of students assigned
                - first_choice_rate: Percentage who got first choice

        Raises:
            Exception: If no students or trips are found in the database.
        """
        # Get all students and trips
        students = Student.query.all()
        trips = Trip.query.all()

        if not students:
            raise Exception("No students found to sort")

        if not trips:
            raise Exception("No trips available for sorting")

        # Reset all student assignments
        for student in students:
            student.trip_id = None

        # Initialize tracking structures
        self._initialize_trip_trackers(trips)

        # Initialize statistics
        self.stats['total'] = len(students)

        # Sort students by priority and process
        priority_students, regular_students = self._categorize_students(students, trips)

        # Randomize for fairness within each group
        random.shuffle(priority_students)
        random.shuffle(regular_students)

        # Process students in priority order
        self._process_student_batch(priority_students)
        self._process_student_batch(regular_students)

        # Calculate final statistics
        self._calculate_final_stats()

        return self.stats

    def _initialize_trip_trackers(self, trips):
        """Initialize tracking structures for all trips.

        Creates tracking dictionaries for each trip to monitor capacity,
        assigned students, dorms, athletic teams, and gender distribution.
        Also organizes trips by type for efficient preference matching.

        Args:
            trips (list): List of Trip objects to initialize tracking for.
        """
        self.trip_trackers = {}
        self.trips_by_type = defaultdict(list)

        for trip in trips:
            self.trip_trackers[trip.id] = {
                'trip': trip,
                'capacity_left': trip.capacity,
                'students': [],
                'dorms': set(),
                'teams': set(),
                'gender_count': {'male': 0, 'female': 0, 'other': 0}
            }
            self.trips_by_type[trip.trip_type].append(trip)

    def _categorize_students(self, students, trips):
        """Separate students into priority and regular groups.

        Students with low comfort levels (<=2) for water or tent activities
        are placed in the priority group to ensure they are assigned to
        compatible trips first.

        Args:
            students (list): List of Student objects to categorize.
            trips (list): List of Trip objects to check for water/tent requirements.

        Returns:
            tuple: (priority_students, regular_students) - Two lists of students.
        """
        priority_students = []
        regular_students = []

        for student in students:
            has_constraints = (
                (any(trip.water for trip in trips) and
                 student.water_comfort and int(student.water_comfort) <= 2) or
                (any(trip.tent for trip in trips) and
                 student.tent_comfort and int(student.tent_comfort) <= 2)
            )

            if has_constraints:
                priority_students.append(student)
            else:
                regular_students.append(student)

        return priority_students, regular_students

    def _process_student_batch(self, students):
        """Process a batch of students for trip assignment.

        Attempts to assign each student to a trip based on their preferences
        in order (first, second, third). If no preferences can be satisfied,
        uses emergency placement to find the best available trip.

        Args:
            students (list): List of Student objects to process.
        """
        for student in students:
            if student.trip_id:  # Already assigned
                continue

            placed = False

            # Try each preference in order
            preferences = [student.trip_pref_1, student.trip_pref_2, student.trip_pref_3]

            for pref_level, preferred_type in enumerate(preferences, 1):
                if not preferred_type:
                    continue

                # Get compatible trips of this type
                compatible_trips = []
                for trip in self.trips_by_type[preferred_type]:
                    if self._can_place_student_in_trip(student, trip):
                        compatible_trips.append(trip)

                if compatible_trips:
                    # Choose trip with most remaining capacity
                    best_trip = max(compatible_trips,
                                  key=lambda t: self.trip_trackers[t.id]['capacity_left'])

                    # Place student
                    self._place_student_in_trip(student, best_trip)

                    # Update statistics
                    self.stats['assigned'] += 1
                    if pref_level == 1:
                        self.stats['first_choice'] += 1
                    elif pref_level == 2:
                        self.stats['second_choice'] += 1
                    elif pref_level == 3:
                        self.stats['third_choice'] += 1

                    placed = True
                    break

            # If no preferences worked, try emergency placement
            if not placed:
                emergency_trip = self._find_emergency_placement(student)
                if emergency_trip:
                    self._place_student_in_trip(student, emergency_trip)
                    self.stats['assigned'] += 1
                    self.stats['no_preference'] += 1

    def _can_place_student_in_trip(self, student, trip):
        """Check if student can be placed in trip without violating constraints.

        Validates that placing the student in the trip would not violate
        any constraints including capacity, water/tent comfort, dorm
        assignments, athletic teams, and gender balance. Uses custom
        criteria order if provided, otherwise uses default order.

        Args:
            student (Student): The student to check placement for.
            trip (Trip): The trip to check placement in.

        Returns:
            bool: True if the student can be placed, False otherwise.
        """
        tracker = self.trip_trackers[trip.id]

        # Always check capacity first
        if tracker['capacity_left'] <= 0:
            return False

        # Build a map of constraint checkers
        # trip preference is handled in batch logic, not as a constraint
        constraint_checkers = {
            'dorm': lambda: not (student.dorm and student.dorm in tracker['dorms']),
            'sports_team': lambda: not (
                student.athletic_team and
                student.athletic_team.lower() not in ['n/a', 'none', '', 'null'] and
                student.athletic_team in tracker['teams']
            ),
            'gender': lambda: self._check_gender_balance(student, trip),
            'trip_preference': lambda: True,
        }
        # Always check water/tent comfort as hard constraints
        if trip.water and student.water_comfort and int(student.water_comfort) <= 2:
            return False
        if trip.tent and student.tent_comfort and int(student.tent_comfort) <= 2:
            return False

        # LOG: Show the custom criteria being used for this sort
        # (remove after debugging)
        if self.custom_criteria:
            print(
                f"[COOTSorter] Using custom criteria order: "
                f"{[c['type'] for c in self.custom_criteria]}"
            )

        # If custom_criteria is set, use its order for constraints
        if self.custom_criteria:
            for crit in self.custom_criteria:
                checker = constraint_checkers.get(crit['type'])
                # LOG: Show which constraint is being checked for this student/trip
                # (remove after debugging)
                if checker:
                    result = checker()
                    print(
                        f"[COOTSorter] Checking {crit['type']} for student "
                        f"{getattr(student, 'student_id', None)} in trip "
                        f"{getattr(trip, 'id', None)}: "
                        f"{'PASS' if result else 'FAIL'}"
                    )
                    if not result:
                        return False
        else:
            # Default: check all constraints in legacy order
            if student.dorm and student.dorm in tracker['dorms']:
                return False
            if (student.athletic_team and
                student.athletic_team.lower() not in ['n/a', 'none', '', 'null'] and
                student.athletic_team in tracker['teams']):
                return False
            if not self._check_gender_balance(student, trip):
                return False
        return True

    def _check_gender_balance(self, student, trip):
        """Check if placing student in trip would maintain gender balance.

        Ensures that the gender distribution in the trip remains balanced.
        The difference between any two gender counts should not exceed 1.
        Prevents adding more than 2 of a single gender when others are at 0
        to encourage diversity.

        Args:
            student (Student): The student to check placement for.
            trip (Trip): The trip to check gender balance for.

        Returns:
            bool: True if placement maintains balance, False otherwise.
        """
        tracker = self.trip_trackers[trip.id]
        current_students = len(tracker['students'])
        if current_students == 0:
            return True  # Empty trip is always balanced

        student_gender = student.gender.lower() if student.gender else 'other'
        current_gender_count = tracker['gender_count'].copy()
        new_gender_count = current_gender_count.copy()
        new_gender_count[student_gender] += 1

        gender_counts = list(new_gender_count.values())
        # Get non-zero counts to check balance between genders that are present
        non_zero_counts = [c for c in gender_counts if c > 0]
        if len(non_zero_counts) > 1:
            # If multiple genders are present, check balance between them
            max_diff = max(non_zero_counts) - min(non_zero_counts)
            if max_diff > 1:
                return False
        # If only one gender is present, prevent adding more than 2 of that gender
        # when others are at 0 (to force gender diversity)
        elif len(non_zero_counts) == 1:
            # Check the current state (before adding) to see if we already have 2+ of one gender
            current_non_zero = [c for c in current_gender_count.values() if c > 0]
            if len(current_non_zero) == 1 and current_non_zero[0] >= 2:
                # We already have 2+ of one gender and 0 of others
                # Only allow adding a different gender (not more of the same)
                current_gender_with_max = [g for g, count in current_gender_count.items()
                                        if count == current_non_zero[0]][0]
                if student_gender == current_gender_with_max:
                    return False

        return True

    def _place_student_in_trip(self, student, trip):
        """Place student in trip and update tracking structures.

        Assigns the student to the trip and updates all tracking structures
        including capacity, dorm sets, athletic team sets, and gender counts.

        Args:
            student (Student): The student to place.
            trip (Trip): The trip to place the student in.
        """
        student.trip_id = trip.id

        tracker = self.trip_trackers[trip.id]

        # Update tracker
        tracker['capacity_left'] -= 1
        tracker['students'].append(student.id)

        if student.dorm:
            tracker['dorms'].add(student.dorm)

        if (student.athletic_team and
            student.athletic_team.lower() not in ['n/a', 'none', '', 'null']):
            tracker['teams'].add(student.athletic_team)

        student_gender = student.gender.lower() if student.gender else 'other'
        tracker['gender_count'][student_gender] += 1

    def _find_emergency_placement(self, student):
        """Find best available trip for student when preferences don't work.

        Scores all available trips based on how well they match the student's
        constraints and preferences. Returns the trip with the highest score
        that has available capacity and meets hard constraints (water/tent comfort).

        Args:
            student (Student): The student needing emergency placement.

        Returns:
            Trip: The best available trip, or None if no suitable trip found.
        """
        best_trip = None
        best_score = -1

        for _, tracker in self.trip_trackers.items():
            trip = tracker['trip']

            # Must have capacity
            if tracker['capacity_left'] <= 0:
                continue

            # Score this trip based on how many constraints it satisfies
            score = 0

            # Water comfort (high priority constraint)
            if not trip.water or not student.water_comfort or int(student.water_comfort) > 2:
                score += 3

            # Tent comfort (high priority constraint)
            if not trip.tent or not student.tent_comfort or int(student.tent_comfort) > 2:
                score += 3

            # Roommate constraint
            if not student.dorm or student.dorm not in tracker['dorms']:
                score += 2

            # Teammate constraint
            if (not student.athletic_team or
                student.athletic_team.lower() in ['n/a', 'none', '', 'null'] or
                student.athletic_team not in tracker['teams']):
                score += 2

            # Gender balance (lower priority for emergency placement)
            current_students = len(tracker['students'])
            if current_students == 0:
                score += 1  # Empty trip is always good for gender balance
            else:
                student_gender = student.gender.lower() if student.gender else 'other'
                temp_count = tracker['gender_count'].copy()
                temp_count[student_gender] += 1
                gender_counts = list(temp_count.values())
                max_diff = max(gender_counts) - min([c for c in gender_counts if c > 0])
                if max_diff <= 1:
                    score += 1

            # Prefer trips with more available capacity
            score += tracker['capacity_left'] * 0.1

            if score > best_score:
                best_score = score
                best_trip = trip

        return best_trip

    def _calculate_final_stats(self):
        """Calculate final placement statistics.

        Computes assignment rate and first choice rate percentages based
        on the sorting results. Updates the stats dictionary with these
        calculated values.
        """
        if self.stats['total'] > 0:
            self.stats['assignment_rate'] = (
                self.stats['assigned'] / self.stats['total']
            ) * 100
            self.stats['first_choice_rate'] = (
                self.stats['first_choice'] / self.stats['total']
            ) * 100

        else:
            self.stats['assignment_rate'] = 0
            self.stats['first_choice_rate'] = 0


# def sort_students(custom_criteria=None):
#     """
#     Main entry point for sorting students.
#     Returns statistics about the sorting process.
#     Accepts optional custom_criteria for sorting priorities.
#     """
#     sorter = COOTSorter(custom_criteria=custom_criteria)
#     return sorter.sort_all_students()


def sort_students(custom_criteria=None):
    """Main entry point for sorting students into trips.

    Runs the sorting algorithm repeatedly until all trips pass validation
    or the maximum number of attempts is reached. Validates each trip after
    sorting to ensure constraints are met. Resets assignments between attempts
    if validation fails.

    Args:
        custom_criteria (list, optional): Custom sorting criteria to use
            for constraint checking order.

    Returns:
        dict: Statistics dictionary from the sorting process, with additional
            keys:
            - attempts: Number of sorting attempts made
            - all_valid: Boolean indicating if all trips passed validation
    """
    # Import validate_trip from views to avoid code duplication
    from .views import validate_trip

    max_attempts = 100  # Prevent infinite loops
    attempt = 0

    while attempt < max_attempts:
        attempt += 1

        # Run the sorting algorithm
        sorter = COOTSorter(custom_criteria=custom_criteria)
        stats = sorter.sort_all_students()

        # Check if all trips are valid
        trips = Trip.query.all()
        all_valid = True

        for trip in trips:
            # Refresh the trip.students relationship to see current assignments
            db.session.expire(trip, ['students'])

            if trip.students:  # Only validate trips with students
                validations = validate_trip(trip)
                if not validations['overall_valid']:
                    all_valid = False
                    break

        # If all trips are valid, we're done!
        if all_valid:
            stats['attempts'] = attempt
            stats['all_valid'] = True
            return stats

        # Reset all assignments for next attempt
        students = Student.query.all()
        for student in students:
            student.trip_id = None

    # Max attempts reached, return the last result
    sorter = COOTSorter(custom_criteria=custom_criteria)
    stats = sorter.sort_all_students()
    stats['attempts'] = max_attempts
    stats['all_valid'] = False
    print(stats)
    return stats
