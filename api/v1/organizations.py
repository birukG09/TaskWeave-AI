"""
TaskWeave AI - Organizations API endpoints
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

organizations_bp = Blueprint('organizations', __name__)

@organizations_bp.route('/', methods=['GET'])
@jwt_required()
def get_organizations():
    """Get user's organizations"""
    current_user_id = get_jwt_identity()
    
    # Mock response for now - will implement with proper models later
    return jsonify([{
        'id': '1',
        'name': 'My Organization',
        'description': 'Default organization',
        'role': 'owner'
    }])

@organizations_bp.route('/', methods=['POST'])
@jwt_required()
def create_organization():
    """Create new organization"""
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    if not data or not data.get('name'):
        return jsonify({'error': 'Organization name is required'}), 400
    
    # Mock response - will implement with proper models later
    return jsonify({
        'id': '1',
        'name': data['name'],
        'description': data.get('description', ''),
        'role': 'owner'
    })