"""
TaskWeave AI - Projects API endpoints
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/<org_id>/projects', methods=['GET'])
@jwt_required()
def get_projects(org_id):
    """Get organization projects"""
    current_user_id = get_jwt_identity()
    
    return jsonify([{
        'id': '1',
        'name': 'Default Project',
        'description': 'Main project workspace',
        'organization_id': org_id
    }])

@projects_bp.route('/<org_id>/projects', methods=['POST'])
@jwt_required()
def create_project(org_id):
    """Create new project"""
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    if not data or not data.get('name'):
        return jsonify({'error': 'Project name is required'}), 400
    
    return jsonify({
        'id': '1',
        'name': data['name'],
        'description': data.get('description', ''),
        'organization_id': org_id
    })