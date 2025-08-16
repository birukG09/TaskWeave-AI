"""
TaskWeave AI - Webhooks API endpoints
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

webhooks_bp = Blueprint('webhooks', __name__)

@webhooks_bp.route('/<org_id>/webhooks', methods=['GET'])
@jwt_required()
def get_webhooks(org_id):
    """Get organization webhooks"""
    current_user_id = get_jwt_identity()
    
    return jsonify([{
        'id': '1',
        'name': 'Slack Webhook',
        'url': '/api/v1/webhooks/slack',
        'events': ['message.created', 'mention.detected'],
        'is_active': True
    }])

@webhooks_bp.route('/slack', methods=['POST'])
def slack_webhook():
    """Handle Slack webhook events"""
    data = request.get_json()
    
    # URL verification for Slack
    if data and data.get('type') == 'url_verification':
        return jsonify({'challenge': data.get('challenge')})
    
    # Process webhook event
    return jsonify({'status': 'received'})