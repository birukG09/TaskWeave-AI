"""
TaskWeave AI - Flask application setup
"""
import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)
migrate = Migrate()
jwt = JWTManager()

def create_app():
    """Application factory"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production-32chars-long')
    
    # Use PostgreSQL from environment (since we have it set up) but with PostgreSQL URL
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith('postgres://'):
        # Convert postgres:// to postgresql:// for SQLAlchemy
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///taskweave.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # JWT Configuration
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', app.config['SECRET_KEY'])
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600  # 1 hour
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = 2592000  # 30 days
    
    # CORS Configuration
    app.config['CORS_ORIGINS'] = ['http://localhost:3000', 'http://localhost:5000']
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Make User model available globally
    from models.user import create_user_model
    global User
    User = create_user_model(db)
    
    # Register blueprints
    from api.v1.auth import auth_bp
    from api.v1.users import users_bp
    from api.v1.organizations import organizations_bp
    from api.v1.projects import projects_bp
    from api.v1.tasks import tasks_bp
    from api.v1.integrations import integrations_bp
    from api.v1.automations import automations_bp
    from api.v1.reports import reports_bp
    from api.v1.webhooks import webhooks_bp
    from api.v1.events import events_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(users_bp, url_prefix='/api/v1/users')
    app.register_blueprint(organizations_bp, url_prefix='/api/v1/orgs')
    app.register_blueprint(projects_bp, url_prefix='/api/v1/orgs')
    app.register_blueprint(tasks_bp, url_prefix='/api/v1/orgs')
    app.register_blueprint(integrations_bp, url_prefix='/api/v1/orgs')
    app.register_blueprint(automations_bp, url_prefix='/api/v1/orgs')
    app.register_blueprint(reports_bp, url_prefix='/api/v1/orgs')
    app.register_blueprint(webhooks_bp, url_prefix='/api/v1/orgs')
    app.register_blueprint(events_bp, url_prefix='/api/v1/orgs')
    
    # Health check endpoint
    @app.route('/healthz')
    def health_check():
        """Health check endpoint"""
        try:
            # Test database connection
            from sqlalchemy import text
            db.session.execute(text('SELECT 1'))
            return {'status': 'healthy', 'version': '1.0.0'}
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {'status': 'unhealthy', 'error': str(e)}, 503
    
    @app.route('/api/v1')
    def api_info():
        """API information endpoint"""
        return {
            'name': 'TaskWeave AI',
            'version': '1.0.0',
            'description': 'AI-powered task automation & orchestration platform',
            'endpoints': {
                'auth': '/api/v1/auth',
                'users': '/api/v1/users',
                'organizations': '/api/v1/orgs',
                'health': '/healthz'
            }
        }
    
    # Create database tables
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)