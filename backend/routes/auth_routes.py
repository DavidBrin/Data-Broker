"""
Authentication routes for user registration, login, and account management.
Handles user creation, password hashing, and session management.
"""
from flask import Blueprint, request, jsonify, session
from models import db, User, UserRole
from werkzeug.security import generate_password_hash
import re

bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def is_valid_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


@bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user account.
    
    Request body:
    {
        "username": "string",
        "email": "string",
        "password": "string",
        "full_name": "string",
        "organization": "string",
        "role": "supplier" | "buyer" | "both",
        "country": "string"
    }
    
    Returns:
        {
            "id": "user_id",
            "username": "username",
            "email": "email",
            "role": "role",
            "message": "Account created successfully"
        }
    """
    data = request.get_json()
    
    # Validation
    if not data.get('username') or not data.get('email') or not data.get('password'):
        return {'error': 'Missing required fields: username, email, password'}, 400
    
    if len(data['password']) < 6:
        return {'error': 'Password must be at least 6 characters'}, 400
    
    if not is_valid_email(data['email']):
        return {'error': 'Invalid email format'}, 400
    
    # Check for existing user
    if User.query.filter_by(username=data['username']).first():
        return {'error': 'Username already exists'}, 409
    
    if User.query.filter_by(email=data['email']).first():
        return {'error': 'Email already exists'}, 409
    
    # Create user
    user = User(
        username=data['username'],
        email=data['email'],
        full_name=data.get('full_name'),
        organization=data.get('organization'),
        country=data.get('country'),
    )
    user.set_password(data['password'])
    
    # Set role
    role = data.get('role', 'supplier').lower()
    if role == 'buyer':
        user.role = UserRole.BUYER.value
        user.is_buyer = True
    elif role == 'both':
        user.role = UserRole.SUPPLIER.value
        user.is_supplier = True
        user.is_buyer = True
    else:  # supplier
        user.role = UserRole.SUPPLIER.value
        user.is_supplier = True
    
    db.session.add(user)
    db.session.commit()
    
    return {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.role,
        'message': 'Account created successfully'
    }, 201


@bp.route('/login', methods=['POST'])
def login():
    """
    Log in a user.
    
    Request body:
    {
        "email": "string",
        "password": "string"
    }
    
    Returns:
        {
            "id": "user_id",
            "username": "username",
            "email": "email",
            "role": "role",
            "is_supplier": bool,
            "is_buyer": bool
        }
    """
    data = request.get_json()
    
    if not data.get('email') or not data.get('password'):
        return {'error': 'Missing email or password'}, 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        return {'error': 'Invalid email or password'}, 401
    
    # In production, would create session/JWT token
    session['user_id'] = user.id
    
    return {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.role,
        'is_supplier': user.is_supplier,
        'is_buyer': user.is_buyer,
        'organization': user.organization,
    }, 200


@bp.route('/logout', methods=['POST'])
def logout():
    """Log out current user."""
    session.pop('user_id', None)
    return {'message': 'Logged out successfully'}, 200


@bp.route('/profile/<user_id>', methods=['GET'])
def get_profile(user_id: str):
    """Get user profile information."""
    user = User.query.get(user_id)
    
    if not user:
        return {'error': 'User not found'}, 404
    
    return {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'full_name': user.full_name,
        'organization': user.organization,
        'role': user.role,
        'is_supplier': user.is_supplier,
        'is_buyer': user.is_buyer,
        'country': user.country,
        'created_at': user.created_at.isoformat(),
    }, 200


@bp.route('/profile/<user_id>', methods=['PUT'])
def update_profile(user_id: str):
    """Update user profile."""
    user = User.query.get(user_id)
    
    if not user:
        return {'error': 'User not found'}, 404
    
    data = request.get_json()
    
    # Update fields
    if 'full_name' in data:
        user.full_name = data['full_name']
    if 'organization' in data:
        user.organization = data['organization']
    if 'country' in data:
        user.country = data['country']
    if 'profile_description' in data:
        user.profile_description = data['profile_description']
    
    db.session.commit()
    
    return {
        'message': 'Profile updated successfully',
        'user': {
            'id': user.id,
            'username': user.username,
            'full_name': user.full_name,
            'organization': user.organization,
            'country': user.country,
        }
    }, 200
