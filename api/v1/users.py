"""
TaskWeave AI - Users API endpoints
"""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User

users_bp = Blueprint('users', __name__)

@users_bp.route('/', methods=['GET'])
@jwt_required()
def get_users():
    """Get all users (admin only - simplified for now)"""
    current_user_id = get_jwt_identity()
    users = User.query.all()
    
    return jsonify([{
        'id': user.id,
        'email': user.email,
        'full_name': user.full_name,
        'is_active': user.is_active
    } for user in users])

@users_bp.route('/<user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Get user by ID"""
    user = User.query.get_or_404(user_id)
    
    return jsonify({
        'id': user.id,
        'email': user.email,
        'full_name': user.full_name,
        'is_active': user.is_active,
        'created_at': user.created_at.isoformat() if user.created_at else None
    })