from models import db, User, Student, Trip
import random
from faker import Faker

fake = Faker()

def add_fake_data():
    # --- Admin ---
    if not User.query.filter_by(email='admin@colby.edu').first():
        admin = User(email='admin@colby.edu', role='admin')
        admin.set_password('1234')
        db.session.add(admin)
        db.session.commit()

    # --- Trips ---
    if Trip.query.count() == 0:
        trip_types = [
            "backpacking", "canoeing", "basecamp", "classic maine camp",
            "local exploration", "specialty basecamp"
        ]
        trips = [
            Trip(
                trip_type=random.choice(trip_types),
                trip_name=f"Trip {i+1} - {fake.city()} Adventure",
                capacity=random.randint(5, 10),
                address=fake.address(),
                water=random.choice([True, False]),
                tent=random.choice([True, False])
            )
            for i in range(10)
        ]
        db.session.add_all(trips)
        db.session.commit()

    # --- Students ---
    if Student.query.count() == 0:
        trip_ids = [trip.id for trip in Trip.query.all()]
        dorms = ["West", "JOPO1", "JOPO2","Johnson", "Leonard"]
        teams = ["Soccer", "Hockey", "Track", "Crew", "None"]

        for i in range(100):
            student = Student(
                student_id=f"S{i+1:03d}",
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.unique.email(),
                trip_id=random.choice(trip_ids),
                trip_pref_1=random.choice(trip_types),
                trip_pref_2=random.choice(trip_types),
                trip_pref_3=random.choice(trip_types),
                dorm=random.choice(dorms),
                athletic_team=random.choice(teams),
                gender=random.choice(["male", "female", "other"]),
                notes=fake.sentence(),
                water_comfort=random.randint(1, 5),
                tent_comfort=random.randint(1, 5),
                hometown=fake.city(),
                poc=random.choice([True, False]),
                fli_international=random.choice([True, False]),
            )
            db.session.add(student)

        db.session.commit()
