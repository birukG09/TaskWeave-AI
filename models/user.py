"""
TaskWeave AI - User model
"""
import uuid
from datetime import datetime

# Define the model function to be called after db initialization
def create_user_model(db):
    """Create User model with database instance"""
    class User(db.Model):
        __tablename__ = "users"
        
        id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
        email = db.Column(db.String(255), unique=True, nullable=False, index=True)
        password_hash = db.Column(db.String(255), nullable=True)  # Nullable for OAuth users
        full_name = db.Column(db.String(255), nullable=True)
        is_active = db.Column(db.Boolean, default=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        def __repr__(self):
            return f"<User {self.email}>"
    
    return User

# Will be initialized in app.py
User = None
