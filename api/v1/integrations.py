"""
TaskWeave AI - Integrations API endpoints
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

integrations_bp = Blueprint('integrations', __name__)

@integrations_bp.route('/<org_id>/integrations', methods=['GET'])
@jwt_required()
def get_integrations(org_id):
    """Get organization integrations"""
    current_user_id = get_jwt_identity()
    
    return jsonify([{
        'id': '1',
        'type': 'slack',
        'name': 'Slack Integration',
        'status': 'connected',
        'last_sync': '2024-01-01T00:00:00Z'
    }])

@integrations_bp.route('/<org_id>/integrations', methods=['POST'])
@jwt_required()
def create_integration(org_id):
    """Create new integration"""
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    if not data or not data.get('type'):
        return jsonify({'error': 'Integration type is required'}), 400
    
    return jsonify({
        'id': '1',
        'type': data['type'],
        'name': f"{data['type'].title()} Integration",
        'status': 'pending',
        'last_sync': None
    })