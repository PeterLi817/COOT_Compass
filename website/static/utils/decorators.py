"""Role-based access control decorators for route protection.

This module provides decorators to restrict route access based on user roles.
Uses a hierarchical role system where higher roles inherit permissions from
lower roles. Roles are ordered: student < admin < admin_manager.
"""

from functools import wraps
from flask import abort
from flask_login import current_user

ROLE_HIERARCHY = {
    'student': 1,
    'admin': 2,
    'admin_manager': 3,
}

def role_required(required_role):
    """Generic decorator for role-based access control.

    Checks if the current user has the required role or higher. Users must
    be authenticated. Returns 401 if not authenticated, 403 if insufficient
    permissions.

    Args:
        required_role (str): The minimum role required to access the route.
            Must be one of: 'student', 'admin', 'admin_manager'.

    Returns:
        function: Decorated function that checks role before execution.

    Raises:
        401: If user is not authenticated.
        403: If user's role is insufficient.
    """
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
    """Decorator requiring admin_manager role.

    Restricts access to routes that require admin_manager privileges.
    This is the highest permission level.

    Args:
        f (function): The route function to protect.

    Returns:
        function: Decorated function that requires admin_manager role.
    """
    return role_required('admin_manager')(f)

def admin_required(f):
    """Decorator requiring admin or admin_manager role.

    Restricts access to routes that require admin privileges or higher.
    Both 'admin' and 'admin_manager' roles can access these routes.

    Args:
        f (function): The route function to protect.

    Returns:
        function: Decorated function that requires admin role or higher.
    """
    return role_required('admin')(f)

def student_required(f):
    """Decorator requiring student role or higher.

    Restricts access to routes that require at least student privileges.
    All authenticated users with any role can access these routes.

    Args:
        f (function): The route function to protect.

    Returns:
        function: Decorated function that requires student role or higher.
    """
    return role_required('student')(f)