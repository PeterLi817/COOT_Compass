from functools import wraps
from flask import abort
from flask_login import current_user

ROLE_HIERARCHY = {
    'student': 1,
    'admin': 2,
    'admin_manager': 3,
}

def role_required(required_role):
    """Generic decorator for role-based access control."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)  # not logged in
            user_level = ROLE_HIERARCHY.get(current_user.role, 0)
            required_level = ROLE_HIERARCHY.get(required_role, 0)
            if user_level < required_level:
                abort(403)  # forbidden
            return f(*args, **kwargs)
        return wrapper
    return decorator

def manager_required(f):
    return role_required('admin_manager')(f)

def admin_required(f):
    return role_required('admin')(f)

def student_required(f):
    return role_required('student')(f)