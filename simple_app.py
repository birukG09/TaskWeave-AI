"""
TaskWeave - Simplified Flask application
"""
import os
import logging
import uuid
from datetime import datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from passlib.context import CryptContext
from sqlalchemy import text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_app():
    """Application factory"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production-32chars-long')
    
    # Use PostgreSQL from environment
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///taskweave.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # JWT Configuration
    app.config['JWT_SECRET_KEY'] = app.config['SECRET_KEY']
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600  # 1 hour
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = 2592000  # 30 days
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app, origins=['http://localhost:3000', 'http://localhost:5000'])
    
    return app

app = create_app()

# Define User model
class User(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=True)
    full_name = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<User {self.email}>"

# Security utilities
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Routes
@app.route('/', methods=['GET'])
def index():
    """Root endpoint - TaskWeave Backend"""
    return {
        'name': 'TaskWeave Backend',
        'version': '1.0.0',
        'description': 'Task automation & orchestration platform',
        'status': 'running',
        'endpoints': {
            'api_info': '/api/v1',
            'auth': '/api/v1/auth',
            'health': '/healthz',
            'docs': '/api/v1'
        }
    }

@app.route('/healthz', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        db.session.execute(text('SELECT 1'))
        return {'status': 'healthy', 'version': '1.0.0'}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {'status': 'unhealthy', 'error': str(e)}, 503

@app.route('/api/v1', methods=['GET'])
def api_info():
    """API information endpoint"""
    return {
        'name': 'TaskWeave',
        'version': '1.0.0',
        'description': 'Task automation & orchestration platform',
        'backend_only': True,
        'database': 'PostgreSQL',
        'authentication': 'JWT',
        'endpoints': {
            'auth': '/api/v1/auth',
            'organizations': '/api/v1/orgs',
            'tasks': '/api/v1/orgs/{org_id}/projects/{project_id}/tasks',
            'integrations': '/api/v1/orgs/{org_id}/integrations',
            'reports': '/api/v1/orgs/{org_id}/reports',
            'webhooks': '/api/v1/webhooks',
            'health': '/healthz'
        }
    }

# Authentication routes
@app.route('/api/v1/auth/register', methods=['POST'])
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
        'refresh_token': refresh_token,
        'user': {
            'id': user.id,
            'email': user.email,
            'full_name': user.full_name
        }
    })

@app.route('/api/v1/auth/login', methods=['POST'])
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
        'refresh_token': refresh_token,
        'user': {
            'id': user.id,
            'email': user.email,
            'full_name': user.full_name
        }
    })

@app.route('/api/v1/auth/me', methods=['GET'])
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

@app.route('/api/v1/auth/refresh', methods=['POST'])
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

# Task routes (mock data for now)
@app.route('/api/v1/orgs/<org_id>/projects/<project_id>/tasks', methods=['GET'])
@jwt_required()
def get_tasks(org_id, project_id):
    """Get project tasks"""
    current_user_id = get_jwt_identity()
    
    return jsonify([{
        'id': '1',
        'title': 'Sample AI-extracted Task',
        'description': 'This task was automatically created from a Slack message using AI',
        'status': 'open',
        'priority': 'medium',
        'project_id': project_id,
        'source': 'slack',
        'created_at': '2024-01-01T00:00:00Z'
    }, {
        'id': '2', 
        'title': 'Review GitHub PR #123',
        'description': 'AI detected this GitHub PR needs review based on team activity',
        'status': 'in_progress',
        'priority': 'high',
        'project_id': project_id,
        'source': 'github',
        'created_at': '2024-01-01T01:00:00Z'
    }])

@app.route('/api/v1/orgs/<org_id>/projects/<project_id>/tasks', methods=['POST'])
@jwt_required()
def create_task(org_id, project_id):
    """Create new task"""
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    if not data or not data.get('title'):
        return jsonify({'error': 'Task title is required'}), 400
    
    # Mock task creation
    task = {
        'id': str(uuid.uuid4()),
        'title': data['title'],
        'description': data.get('description', ''),
        'status': 'open',
        'priority': data.get('priority', 'medium'),
        'project_id': project_id,
        'source': 'manual',
        'created_at': datetime.utcnow().isoformat()
    }
    
    return jsonify(task), 201

# Organization routes (mock data)
@app.route('/api/v1/orgs', methods=['GET'])
@jwt_required()
def get_organizations():
    """Get user's organizations"""
    current_user_id = get_jwt_identity()
    
    return jsonify([{
        'id': '1',
        'name': 'My Organization',
        'description': 'Default organization for TaskWeave AI',
        'role': 'owner'
    }])

# Integration routes (mock data)
@app.route('/api/v1/orgs/<org_id>/integrations', methods=['GET'])
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
    }, {
        'id': '2',
        'type': 'github', 
        'name': 'GitHub Integration',
        'status': 'connected',
        'last_sync': '2024-01-01T00:30:00Z'
    }])

# Reports routes (mock data)
@app.route('/api/v1/orgs/<org_id>/reports', methods=['GET'])
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
        'summary': 'Automated summary: This week your team completed 8 tasks, with 3 high-priority items resolved. Slack activity increased by 20% and 5 new GitHub issues were created.'
    }])

# Webhooks
@app.route('/api/v1/webhooks/slack', methods=['POST'])
def slack_webhook():
    """Handle Slack webhook events"""
    data = request.get_json()
    
    # URL verification for Slack
    if data and data.get('type') == 'url_verification':
        return jsonify({'challenge': data.get('challenge')})
    
    # Process webhook event - trigger AI task extraction
    if data and data.get('event', {}).get('text'):
        try:
            from tasks.analysis_tasks import process_slack_message_for_tasks
            result = process_slack_message_for_tasks.delay(data.get('event'))
            logger.info(f"Slack message queued for processing: {result.id}")
        except Exception as e:
            logger.error(f"Failed to queue Slack message: {e}")
    
    logger.info(f"Slack webhook received: {data}")
    return jsonify({'status': 'received'})

# Text Analysis Endpoints  
@app.route('/api/v1/analyze-text', methods=['POST'])
@jwt_required()
def analyze_text_for_tasks():
    """Analyze text for task extraction"""
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    if not data or not data.get('text'):
        return jsonify({'error': 'Text is required'}), 400
    
    try:
        from analysis_service import analysis_service
        tasks = analysis_service.extract_tasks_from_text(
            text=data['text'],
            source=data.get('source', 'manual')
        )
        
        return jsonify({
            'status': 'success',
            'tasks_extracted': len(tasks),
            'tasks': tasks
        })
    except Exception as e:
        logger.error(f"Text analysis failed: {e}")
        return jsonify({'error': 'Text analysis temporarily unavailable'}), 503

@app.route('/api/v1/generate-report', methods=['POST'])
@jwt_required()
def generate_report():
    """Generate automated report"""
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    try:
        from tasks.report_tasks import generate_weekly_report
        result = generate_weekly_report.delay(
            org_id=data.get('org_id', 'default_org'),
            project_id=data.get('project_id')
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Report generation started',
            'task_id': result.id
        }), 202
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        return jsonify({'error': 'Report generation failed'}), 500

# Scheduler Management Endpoints
@app.route('/api/v1/scheduler/jobs', methods=['GET'])
@jwt_required()
def get_scheduled_jobs():
    """Get status of all scheduled jobs"""
    try:
        from scheduler import task_scheduler
        jobs = task_scheduler.get_job_status()
        return jsonify({'jobs': jobs})
    except Exception as e:
        logger.error(f"Failed to get scheduler status: {e}")
        return jsonify({'error': 'Scheduler status unavailable'}), 500

@app.route('/api/v1/scheduler/trigger/<job_name>', methods=['POST'])
@jwt_required()
def trigger_scheduled_job(job_name):
    """Manually trigger a scheduled job"""
    current_user_id = get_jwt_identity()
    
    job_map = {
        'daily_summary': 'tasks.slack_tasks.send_daily_summary',
        'weekly_report': 'tasks.report_tasks.generate_weekly_report',
        'productivity_analysis': 'tasks.analysis_tasks.analyze_team_productivity',
        'notion_sync': 'tasks.notion_tasks.bulk_sync_tasks_to_notion'
    }
    
    if job_name not in job_map:
        return jsonify({'error': 'Invalid job name'}), 400
    
    try:
        if job_name == 'daily_summary':
            from tasks.slack_tasks import send_daily_summary
            result = send_daily_summary.delay('default_org')
        elif job_name == 'weekly_report':
            from tasks.report_tasks import generate_weekly_report
            result = generate_weekly_report.delay('default_org')
        elif job_name == 'productivity_analysis':
            from tasks.analysis_tasks import analyze_team_productivity
            result = analyze_team_productivity.delay('default_org')
        elif job_name == 'notion_sync':
            from tasks.notion_tasks import bulk_sync_tasks_to_notion
            result = bulk_sync_tasks_to_notion.delay([])
        
        return jsonify({
            'status': 'success',
            'message': f'Job {job_name} triggered',
            'task_id': result.id
        }), 202
    except Exception as e:
        logger.error(f"Failed to trigger job {job_name}: {e}")
        return jsonify({'error': f'Failed to trigger {job_name}'}), 500

# Background Task Status Endpoint
@app.route('/api/v1/tasks/status/<task_id>', methods=['GET'])
@jwt_required()
def get_task_status(task_id):
    """Get status of background task"""
    try:
        from celery_app import celery
        result = celery.AsyncResult(task_id)
        
        return jsonify({
            'task_id': task_id,
            'status': result.status,
            'result': result.result if result.ready() else None
        })
    except Exception as e:
        logger.error(f"Failed to get task status: {e}")
        return jsonify({'error': 'Task status unavailable'}), 500

# Initialize database
with app.app_context():
    try:
        db.create_all()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")

if __name__ == '__main__':
    # Start the scheduler when running the app (with error handling)
    try:
        from scheduler import task_scheduler
        task_scheduler.start()
        logger.info("Task scheduler started successfully")
    except Exception as e:
        logger.warning(f"Scheduler startup failed: {e}")
    
    app.run(host='0.0.0.0', port=5000, debug=True)