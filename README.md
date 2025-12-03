# COOT Compass

A Flask web application for managing Colby Outdoor Orientation Trips (COOT) student assignments and trip groups. This system helps coordinate outdoor orientation trips by intelligently assigning first-year students to trips based on their preferences while maintaining balanced group compositions.

## Features

### Student Management
- Add, remove, and manage first-year student information
- Track student preferences for trip types (backpacking, canoeing, basecamp, etc.)
- Store detailed student profiles including:
  - Dorm assignments and roommate information
  - Athletic team affiliations
  - Water and tent comfort levels (1-5 scale)
  - Hometown and demographic information
  - Special notes and considerations

### Trip Management
- View and organize trips with real-time capacity tracking
- Support for multiple trip types:
  - Backpacking
  - Canoeing
  - Basecamp
  - Classic Maine Camp
  - Local Exploration
  - Specialty Basecamp
- Track trip-specific requirements (water exposure, tent camping)

### Intelligent Assignment System
- Automated student sorting algorithm that considers:
  - Student trip preferences (1st, 2nd, 3rd choice)
  - Gender ratio balance
  - Athletic team distribution (avoiding same-team clustering)
  - Dorm/roommate separation
  - Water and tent comfort level matching
- Manual assignment override capabilities
- Move and swap students between trips

### Trip Validation
- Real-time validation of group compositions
- Automatic checking of:
  - Gender ratio balance (within acceptable ranges)
  - Athletic team distribution
  - Dorm/roommate conflicts
  - Comfort level appropriateness
- Visual indicators for validation status

### Data Management
- CSV import for bulk student and trip data uploads
- Export capabilities for reporting
- Database reset and management tools (admin only)

### User Authentication & Authorization
- Secure OAuth-based login system
- Role-based access control:
  - **Admin Manager**: Full system access including user management and database operations
  - **Admin**: Can view and edit all data except admin management
  - **Student**: Limited view of own trip assignment (when enabled)
- Integration with institutional authentication systems

### API
- RESTful API endpoints for programmatic access
- JSON responses for all data operations
- Protected endpoints with authentication requirements

## Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/PeterLi817/COOT_Compass.git
cd COOT_Compass
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with the following variables:
```env
SECRET_KEY=your-secret-key-here
ENVIRONMENT=development  # or 'production'
SQLALCHEMY_DATABASE_URI=sqlite:///instance/database.db  # or PostgreSQL URI for production
```

5. Initialize the database:
```bash
python app.py
```

6. Access the application at `http://localhost:5000`

## Usage

### For Administrators

1. **Login**: Access the system using your institutional credentials
2. **View Groups**: Navigate to the Groups page to see all trips with student assignments and validation status
3. **Manage Students**:
   - Go to the First Years page to add, remove, or update student information
   - Upload CSV files for bulk student imports
4. **Assign Students**:
   - Use the auto-sort feature to intelligently assign all students
   - Manually move or swap students between trips as needed
   - View validation warnings and adjust assignments accordingly
5. **Manage Trips**:
   - View trip capacity and current assignments
   - Monitor trip type distribution
6. **Settings**:
   - Toggle student view access
   - Manage admin users
   - Clear database (admin manager only)

### For Students

1. **Login**: Access the system using your institutional credentials
2. **View Assignment**: See your assigned trip (when administrators enable student view)

## Tech Stack

### Backend
- **Flask 3.1.2** - Modern Python web framework
- **SQLAlchemy 2.0.44** - SQL toolkit and ORM
- **Flask-Login 0.6.3** - User session management
- **Flask-SQLAlchemy 3.1.1** - Flask integration for SQLAlchemy
- **Authlib 1.6.5** - OAuth authentication library

### Database
- **SQLite** - Development database (file-based)
- **PostgreSQL** - Production database (via psycopg2-binary)

### Additional Libraries
- **Faker 38.0.0** - Development data generation
- **python-dotenv 1.2.1** - Environment variable management
- **Werkzeug 3.1.3** - WSGI utilities
- **Jinja2 3.1.6** - Template engine
- **gunicorn** - Production WSGI server

### Frontend
- **HTML5/CSS3** - Modern responsive design
- **JavaScript (ES6+)** - Client-side interactivity
- **Fetch API** - Asynchronous data operations

## Project Structure

```
COOT_Compass/
├── app.py                      # Application entry point
├── requirements.txt            # Python dependencies
├── runtime.txt                 # Python version for deployment
├── Procfile                    # Heroku deployment configuration
├── .env                        # Environment variables (not in repo)
├── instance/                   # Instance-specific files (database)
│   └── database.db            # SQLite database file
├── tests/                      # Test suite
│   ├── conftest.py            # Test configuration and fixtures
│   ├── unit/                  # Unit tests
│   └── functional/            # Functional/integration tests
└── website/                    # Main application package
    ├── __init__.py            # App factory and configuration
    ├── models.py              # Database models (User, Student, Trip, AppSettings)
    ├── views.py               # Main application routes and view logic
    ├── auth.py                # Authentication routes and OAuth setup
    ├── api_routes.py          # RESTful API endpoints
    ├── sort.py                # Intelligent student sorting algorithm
    ├── fill_db.py             # Development database seeding utilities
    ├── static/                # Static assets
    │   ├── css/
    │   │   └── styles.css     # Application styles
    │   ├── js/
    │   │   ├── api-client.js  # API communication utilities
    │   │   ├── first-years.js # First-years page functionality
    │   │   ├── groups.js      # Groups/trips page functionality
    │   │   ├── login.js       # Login page functionality
    │   │   ├── settings.js    # Settings page functionality
    │   │   └── trips.js       # Trip management functionality
    │   ├── img/               # Image assets
    │   └── utils/
    │       └── decorators.py  # Custom route decorators (role-based access)
    └── templates/             # Jinja2 HTML templates
        ├── login.html         # Login page
        ├── first-years.html   # Student management page
        ├── groups.html        # Trip groups overview (admin)
        ├── trips.html         # Trip management page
        ├── settings.html      # Admin settings page
        ├── student_view.html  # Student trip assignment view
        └── no_view.html       # Access denied page
```

## Database Models

### User
- Email (primary key)
- First and last name
- Role (admin_manager, admin, student, or None)
- One-to-one relationship with Student

### Student
- Student ID and personal information
- Trip preferences (1st, 2nd, 3rd choice)
- Dorm assignment and roommate info
- Athletic team affiliation
- Gender and demographic information
- Water and tent comfort levels (1-5)
- Notes and special considerations
- Foreign key to Trip (many-to-one)
- Foreign key to User (one-to-one)

### Trip
- Trip name and type
- Capacity and current assignments
- Location/address
- Water and tent requirements (boolean flags)
- One-to-many relationship with Students

### AppSettings
- System-wide configuration
- Student view visibility toggle

## API Endpoints

All API endpoints are prefixed with `/api` and require authentication.

- `GET /api/health` - Health check (public)
- `GET /api/students` - Get all students (admin required)
- `GET /api/trips` - Get all trips (admin required)
- `POST /api/students` - Add new student (admin required)
- `PUT /api/students/<id>` - Update student (admin required)
- `DELETE /api/students/<id>` - Remove student (admin required)
- `POST /api/sort` - Run auto-sort algorithm (admin required)
- `POST /api/assign` - Manual student assignment (admin required)

## Deployment

The application is configured for deployment to Heroku or similar PaaS platforms:

1. Ensure `Procfile` and `runtime.txt` are present
2. Set environment variables on your hosting platform
3. Use PostgreSQL for production database
4. The app will automatically handle `postgres://` to `postgresql://` URI conversion

## Development

### Adding Fake Data

For development and testing, you can populate the database with fake data:

```python
from website.fill_db import add_fake_data
add_fake_data(num_students=50, num_trips=10)
```

### Running Tests

```bash
pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write or update tests as needed
5. Submit a pull request

## License

This project is developed for Colby College COOT program.

## Support

For issues or questions, please contact the development team or create an issue in the GitHub repository.