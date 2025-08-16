"""
TaskWeave AI - Automations API endpoints  
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

automations_bp = Blueprint('automations', __name__)

@automations_bp.route('/<org_id>/automations', methods=['GET'])
@jwt_required()
def get_automations(org_id):
    """Get organization automations"""
    current_user_id = get_jwt_identity()
    
    return jsonify([{
        'id': '1',
        'name': 'Auto-create tasks from Slack',
        'description': 'Automatically create tasks from Slack messages with @todo',
        'trigger': 'slack_message',
        'action': 'create_task',
        'is_active': True
    }])

@automations_bp.route('/<org_id>/automations', methods=['POST'])
@jwt_required()
def create_automation(org_id):
    """Create new automation"""
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    if not data or not data.get('name'):
        return jsonify({'error': 'Automation name is required'}), 400
    
    return jsonify({
        'id': '1',
        'name': data['name'],
        'description': data.get('description', ''),
        'trigger': data.get('trigger'),
        'action': data.get('action'),
        'is_active': True
    })