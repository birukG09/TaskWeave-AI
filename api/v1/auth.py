"""
TaskWeave AI - Authentication API endpoints
"""
from flask import Blueprint, request, jsonify, redirect, url_for
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
import secrets
import logging

from models.user import User
from app import db
from auth.security import get_password_hash, verify_password
from services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

@auth_bp.route("/register", methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400
    
    # Check if user already exists
    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({'error': 'Email already registered'}), 400
    
    # Create new user
    password_hash = get_password_hash(data['password'])
    user = User(
        email=data['email'],
        password_hash=password_hash,
        full_name=data.get('full_name'),
        is_active=True
    )
    
    db.session.add(user)
    db.session.commit()
    
    # Generate tokens
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    
    logger.info(f"User registered: {user.id}, {user.email}")
    
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token
    })

@auth_bp.route("/login", methods=['POST'])
def login():
    """Login user with email and password"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400
    
    # Find user
    user = User.query.filter_by(email=data['email']).first()
    if not user or not user.password_hash:
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Verify password
    if not verify_password(data['password'], user.password_hash):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Generate tokens
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    
    logger.info(f"User logged in: {user.id}, {user.email}")
    
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token
    })

@auth_bp.route("/refresh", methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    """Refresh access token"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 401
    
    # Generate new tokens
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token
    })

@auth_bp.route("/logout", methods=['POST'])
@jwt_required()
def logout():
    """Logout user (client should discard tokens)"""
    current_user_id = get_jwt_identity()
    logger.info(f"User logged out: {current_user_id}")
    return jsonify({'message': 'Logged out successfully'})

@auth_bp.route("/me", methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user info"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'id': user.id,
        'email': user.email,
        'full_name': user.full_name,
        'is_active': user.is_active,
        'created_at': user.created_at.isoformat() if user.created_at else None
    })
