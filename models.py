from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# -----------------------
# USER MODEL
# -----------------------
class User(db.Model, UserMixin):
    __tablename__ = 'users'

    email = db.Column(db.String(120), primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20))  # admin, student, or none

    # One-to-one relationship with Student
    student = db.relationship('Student', backref='user', uselist=False)

    def get_id(self):
        """Override get_id to return email instead of id for Flask-Login."""
        return self.email

    def set_password(self, password):
        """Hash the password and store it."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User email='{self.email}' role='{self.role}'>"


# -----------------------
# STUDENT MODEL
# -----------------------
class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id', ondelete='SET NULL'), nullable=True)

    trip_pref_1 = db.Column(db.String(50)) # backpacking, canoeing, basecamp, classic maine camp, local exploration, or specialty basecamp
    trip_pref_2 = db.Column(db.String(50))
    trip_pref_3 = db.Column(db.String(50))
    dorm = db.Column(db.String(50)) # Dana, West, East, JOPO, etc
    athletic_team = db.Column(db.String(50))
    gender = db.Column(db.String(20)) # male, female, other
    notes = db.Column(db.Text)
    water_comfort = db.Column(db.Integer) # 1-5
    tent_comfort = db.Column(db.Integer) # 1-5
    hometown = db.Column(db.String(100))
    poc = db.Column(db.Boolean)
    fli_international = db.Column(db.Boolean)

    # One-to-one with User (nullable since not all students may have accounts).
    # NOTE: There is also a separate 'email' field for the student's own email address.
    # If you truly want strict 1:1 (no two students linked to same user), add unique=True.
    user_email = db.Column(db.String(120), db.ForeignKey('users.email', ondelete='SET NULL'), nullable=True, unique=True)

    def __repr__(self):
        return f"<Student id={self.id} name='{self.first_name} {self.last_name}' trip_id={self.trip_id}>"


# -----------------------
# TRIP MODEL
# -----------------------
class Trip(db.Model):
    __tablename__ = 'trips'

    id = db.Column(db.Integer, primary_key=True)
    trip_type = db.Column(db.String(50), nullable=False)  # backpacking, canoeing, basecamp, classic maine camp, local exploration, specialty basecamp
    trip_name = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(200))
    water = db.Column(db.Boolean, default=False)
    tent = db.Column(db.Boolean, default=False)

    # One-to-many: Trip → Students
    # Note: cascade='all, delete-orphan' will delete students only if they become orphaned
    # Setting trip_id to NULL when trip is deleted (via ondelete='SET NULL') is safer
    students = db.relationship('Student', backref='trip')

    def __repr__(self):
        return f"<Trip id={self.id} name='{self.trip_name}' type='{self.trip_type}' capacity={self.capacity}>"
