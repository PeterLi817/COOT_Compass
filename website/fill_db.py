"""Database seeding utility for development and testing.

This module provides functions to populate the database with fake data
for development and testing purposes. Uses the Faker library to generate
realistic test data for students and trips.
"""
import random
from faker import Faker

from website import db
from .models import Student, Trip

fake = Faker()

def add_fake_data():
    """Generate and add fake data to the database for development.

    Creates fake trips and students with realistic distributions:
    - 11 trips with various types (backpacking, canoeing, basecamp, etc.)
    - 100 students with diverse attributes including:
        - Gender distribution: 5% 'other', otherwise 50/50 male/female
        - Athletic teams: 30% assigned to one of 30 teams
        - Trip preferences: 3 unique preferences per student
        - Comfort levels: 20% low comfort (1-2), 80% high comfort (3-5)
        - POC and FLI flags: 20% each

    Only adds data if the respective tables are empty. This prevents
    duplicate data when called multiple times.
    """
    # --- Admin ---
    # if not User.query.filter_by(email='admin@colby.edu').first():
    #     admin = User(email='admin@colby.edu', first_name='Admin', last_name='User', role='admin')
    #     admin.set_password('1234')
    #     db.session.add(admin)
    #     db.session.commit()
    #     print('added')

    # Common trip definitions
    trip_types = [
        "backpacking", "canoeing", "basecamp", "classic maine camp",
        "local exploration", "specialty basecamp"
    ]
    water_probs = {"canoeing": 1.0, "specialty basecamp": 0.75, "local exploration": 0.15}
    tent_types = {"backpacking", "canoeing", "basecamp", "specialty basecamp"}

    # --- Trips ---
    if Trip.query.count() == 0:
        trips = []

        for i in range(11):
            t = random.choice(trip_types)
            trips.append(
                Trip(
                    trip_type=t,
                    trip_name=f"Trip {i+1} - {fake.city()} Adventure",
                    capacity=10,
                    address=fake.address(),
                    water=random.random() < water_probs.get(t, 0),
                    tent=(t in tent_types)
                )
            )
        db.session.add_all(trips)
        db.session.commit()

    # --- Students ---
    if Student.query.count() == 0:
        teams = [f"Team {i}" for i in range(1, 31)]

        for i in range(100):
            # Gender: 5% 'other', otherwise 50/50 male/female
            r = random.random()
            if r < 0.05:
                gender = "other"
            else:
                gender = "male" if random.random() < 0.5 else "female"

            # Athletic team: 30% chance assigned to one of 30 teams, else None
            athletic_team = random.choice(teams) if random.random() < 0.30 else None

            # Trip preferences: choose 3 unique types (no repeats)
            prefs = random.sample(trip_types, k=min(3, len(trip_types)))

            # Comfort distributions: 20% in [1,2], 80% in [3,5]
            water_comfort = random.randint(1, 2) if random.random() < 0.20 else random.randint(3, 5)
            tent_comfort = random.randint(1, 2) if random.random() < 0.20 else random.randint(3, 5)

            # POC and FLI: 20% True each
            poc_flag = random.random() < 0.20
            fli_flag = random.random() < 0.20

            student = Student(
                student_id=f"S{i+1:03d}",
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.unique.email(),
                # trip_id=random.choice(trip_ids),
                trip_pref_1=prefs[0] if len(prefs) > 0 else None,
                trip_pref_2=prefs[1] if len(prefs) > 1 else None,
                trip_pref_3=prefs[2] if len(prefs) > 2 else None,
                dorm=f'dorm {random.randint(1,250)}',
                athletic_team=athletic_team,
                gender=gender,
                notes=random.choice([None,fake.sentence()]),
                water_comfort=water_comfort,
                tent_comfort=tent_comfort,
                hometown=fake.city(),
                poc=poc_flag,
                fli_international=fli_flag,
            )
            db.session.add(student)

        db.session.commit()
