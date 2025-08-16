"""
TaskWeave AI - Reports API endpoints
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/<org_id>/reports', methods=['GET'])
@jwt_required()
def get_reports(org_id):
    """Get organization reports"""
    current_user_id = get_jwt_identity()
    
    return jsonify([{
        'id': '1',
        'title': 'Weekly Progress Report',
        'type': 'progress',
        'period': 'weekly',
        'generated_at': '2024-01-01T00:00:00Z',
        'summary': 'AI-generated summary of team progress this week'
    }])

@reports_bp.route('/<org_id>/reports/generate', methods=['POST'])
@jwt_required()
def generate_report(org_id):
    """Generate new report"""
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    report_type = data.get('type', 'progress')
    
    return jsonify({
        'id': '1',
        'title': f'{report_type.title()} Report',
        'type': report_type,
        'period': data.get('period', 'weekly'),
        'generated_at': '2024-01-01T00:00:00Z',
        'summary': f'AI-generated {report_type} report for your team'
    })