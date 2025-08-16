"""
TaskWeave AI - Events API endpoints
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

events_bp = Blueprint('events', __name__)

@events_bp.route('/<org_id>/events', methods=['GET'])
@jwt_required()
def get_events(org_id):
    """Get organization events"""
    current_user_id = get_jwt_identity()
    
    return jsonify([{
        'id': '1',
        'type': 'task_created',
        'source': 'slack',
        'description': 'Task created from Slack message',
        'created_at': '2024-01-01T00:00:00Z',
        'metadata': {
            'channel': '#general',
            'user': 'john.doe'
        }
    }])

@events_bp.route('/<org_id>/events/process', methods=['POST'])
@jwt_required()
def process_events(org_id):
    """Manually trigger event processing"""
    current_user_id = get_jwt_identity()
    
    return jsonify({
        'message': 'Event processing triggered',
        'processed': 5,
        'created_tasks': 2
    })