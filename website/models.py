"""Database models for COOT Compass.

This module defines all SQLAlchemy database models including User, Student,
Trip, and AppSettings. These models represent the core data structures
of the application.
"""

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from website import db

class User(db.Model, UserMixin):
    """User model representing application users.

    Users can have roles: 'admin_manager', 'admin', 'student', or None.
    Admin managers have the highest privileges and can manage other admins.
    Users are linked to Student records via a one-to-one relationship.

    Attributes:
        email (str): Primary key, user's email address.
        first_name (str): User's first name.
        last_name (str): User's last name.
        role (str): User's role in the system. Can be 'admin_manager',
            'admin', 'student', or None.
        student (Student): One-to-one relationship with Student record.
    """
    __tablename__ = 'users'

    email = db.Column(db.String(120), primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20))  # admin, admin_manager, student, or None
    # Admins can see and edit data, only admin managers can edit admins or clear the database

    # One-to-one relationship with Student
    student = db.relationship('Student', backref='user', uselist=False)

    def get_id(self):
        """Override get_id to return email instead of id for Flask-Login.

        Flask-Login requires this method to identify the user in the session.
        We use email as the identifier instead of a numeric ID.

        Returns:
            str: The user's email address.
        """
        return self.email

    def set_password(self, password):
        """Hash and store a password for the user.

        Args:
            password (str): The plain text password to hash and store.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify a password against the stored hash.

        Args:
            password (str): The plain text password to verify.

        Returns:
            bool: True if the password matches, False otherwise.
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User email='{self.email}' role='{self.role}'>"


class Student(db.Model):
    """Student model representing first-year students in the COOT program.

    Students have various attributes including preferences, comfort levels,
    and demographic information. They are assigned to trips and can be
    linked to User accounts for authentication.

    Attributes:
        id (int): Primary key, auto-incrementing integer.
        student_id (str): Unique student identifier.
        first_name (str): Student's first name.
        last_name (str): Student's last name.
        email (str): Student's email address (unique).
        trip_id (int): Foreign key to assigned Trip (nullable).
        trip_pref_1 (str): First trip preference type.
        trip_pref_2 (str): Second trip preference type.
        trip_pref_3 (str): Third trip preference type.
        dorm (str): Student's dormitory name.
        athletic_team (str): Student's athletic team name.
        gender (str): Student's gender ('male', 'female', or 'other').
        notes (str): Additional notes about the student.
        water_comfort (int): Water activity comfort level (1-5).
        tent_comfort (int): Tent camping comfort level (1-5).
        hometown (str): Student's hometown.
        poc (bool): Person of color flag.
        fli_international (bool): First-generation/low-income/international flag.
        user_email (str): Foreign key to User account (nullable, unique).
    """
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id', ondelete='SET NULL'), nullable=True)
    # Trip preferences: backpacking, canoeing, basecamp, classic maine camp,
    # local exploration, or specialty basecamp
    trip_pref_1 = db.Column(db.String(50))
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
    user_email = db.Column(
        db.String(120),
        db.ForeignKey('users.email', ondelete='SET NULL'),
        nullable=True,
        unique=True,
    )

    def __repr__(self):
        return (
            f"<Student id={self.id} "
            f"name='{self.first_name} {self.last_name}' "
            f"trip_id={self.trip_id}>"
        )



class Trip(db.Model):
    """Trip model representing COOT orientation trips.

    Trips have a type, capacity, and various attributes. Students are
    assigned to trips, and trips can have water activities and/or tent camping.

    Attributes:
        id (int): Primary key, auto-incrementing integer.
        trip_type (str): Type of trip (e.g., 'backpacking', 'canoeing',
            'basecamp', 'classic maine camp', 'local exploration',
            'specialty basecamp').
        trip_name (str): Name of the trip.
        capacity (int): Maximum number of students for this trip.
        address (str): Trip location address.
        water (bool): Whether the trip involves water activities.
        tent (bool): Whether the trip involves tent camping.
        students (list): One-to-many relationship with Student records.
    """
    __tablename__ = 'trips'

    id = db.Column(db.Integer, primary_key=True)
    # Trip types include: # backpacking, canoeing, basecamp,
    # classic maine camp, local exploration, specialty basecamp
    trip_type = db.Column(db.String(50), nullable=False)
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
        return (
            f"<Trip id={self.id} "
            f"name='{self.trip_name}' "
            f"type='{self.trip_type}' "
            f"capacity={self.capacity}>"
        )


class AppSettings(db.Model):
    """Application settings model for storing global configuration.

    This model uses a singleton pattern to ensure there is always exactly
    one settings record in the database. Currently stores the setting for
    whether trips should be visible to students.

    Attributes:
        id (int): Primary key, auto-incrementing integer.
        show_trips_to_students (bool): Whether trips are visible to students
            in their view.
    """
    __tablename__ = 'app_settings'

    id = db.Column(db.Integer, primary_key=True)
    show_trips_to_students = db.Column(db.Boolean, nullable=False, default=False)

    @classmethod
    def get(cls):
        """Get the application settings singleton instance.

        Ensures there is always exactly one settings record in the database.
        If no settings exist, creates a new record with default values.

        Returns:
            AppSettings: The single AppSettings instance.
        """
        settings = cls.query.first()
        if not settings:
            settings = cls(show_trips_to_students=False)
            db.session.add(settings)
            db.session.commit()
        return settings
