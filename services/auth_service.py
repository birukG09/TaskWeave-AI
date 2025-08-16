"""
TaskWeave AI - Authentication service
"""
from typing import Dict, Any
from sqlalchemy.orm import Session
import structlog

from models.user import User
from schemas.user import UserCreate
from auth.security import get_password_hash

logger = structlog.get_logger()

class AuthService:
    def __init__(self, db: Session):
        self.db = db
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        user = User(
            email=user_data.email,
            name=user_data.name,
            password_hash=get_password_hash(user_data.password),
            role=user_data.role
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    async def find_or_create_oauth_user(self, user_info: Dict[str, Any]) -> User:
        """Find existing user or create new one from OAuth data"""
        email = user_info.get("email")
        if not email:
            raise ValueError("Email is required for OAuth users")
        
        # Try to find existing user
        user = self.db.query(User).filter(User.email == email).first()
        
        if user:
            # Update user info if needed
            if user_info.get("name") and not user.name:
                user.name = user_info["name"]
                self.db.commit()
                self.db.refresh(user)
            return user
        
        # Create new OAuth user
        user = User(
            email=email,
            name=user_info.get("name"),
            password_hash=None  # OAuth users don't have passwords
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        logger.info("OAuth user created", user_id=str(user.id), email=email, provider=user_info.get("provider"))
        
        return user
