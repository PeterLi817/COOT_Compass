# COOT Compass

A Flask web application for managing Colby Outdoor Orientation Trips (COOT) student assignments and trip groups.

## Features

- **Student Management**: Add, remove, and manage first-year student information
- **Trip Management**: View and organize trips with capacity tracking
- **Group Assignment**: Assign students to trips and validate group compositions
- **Trip Validation**: Automatic validation of:
  - Gender ratio balance
  - Athletic team distribution
  - Dorm/roommate separation
  - Water and tent comfort levels
- **CSV Import**: Bulk upload students and trips via CSV file
- **User Authentication**: Secure login system with role-based access (admin/student)

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Access the application at `http://localhost:5000`

## Usage

1. **Login**: Use your credentials to access the system
2. **View Groups**: See all trips with student assignments and validation status
3. **Manage Students**: Add, remove, or update student information on the First Years page
4. **Assign Students**: Move or swap students between trips
5. **Upload CSV**: Import student and trip data in bulk

## Tech Stack

- **Flask** - Web framework
- **SQLAlchemy** - Database ORM
- **Flask-Login** - User authentication
- **SQLite** - Database (development)

## Project Structure

- `app.py` - Main application entry point
- `models.py` - Database models (User, Student, Trip)
- `views.py` - Main application routes and logic
- `auth.py` - Authentication routes
- `fill_db.py` - Development data seeding
- `templates/` - HTML templates
- `static/` - CSS and JavaScript assets