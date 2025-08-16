"""
TaskWeave AI - Tasks API endpoints
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/<org_id>/projects/<project_id>/tasks', methods=['GET'])
@jwt_required()
def get_tasks(org_id, project_id):
    """Get project tasks"""
    current_user_id = get_jwt_identity()
    
    return jsonify([{
        'id': '1',
        'title': 'Sample Task',
        'description': 'AI-extracted task from Slack message',
        'status': 'open',
        'priority': 'medium',
        'project_id': project_id,
        'source': 'slack'
    }])

@tasks_bp.route('/<org_id>/projects/<project_id>/tasks', methods=['POST'])
@jwt_required()
def create_task(org_id, project_id):
    """Create new task"""
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    if not data or not data.get('title'):
        return jsonify({'error': 'Task title is required'}), 400
    
    return jsonify({
        'id': '1',
        'title': data['title'],
        'description': data.get('description', ''),
        'status': 'open',
        'priority': data.get('priority', 'medium'),
        'project_id': project_id
    })