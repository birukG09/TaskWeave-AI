"""
TaskWeave AI - Organization service
"""
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import structlog

from models.user import User
from models.organization import Organization, Membership
from schemas.organization import OrganizationCreate, OrganizationUpdate, MembershipCreate

logger = structlog.get_logger()

class OrganizationService:
    def __init__(self, db: Session):
        self.db = db
    
    async def create_organization(self, org_data: OrganizationCreate, owner_id: str) -> Organization:
        """Create a new organization"""
        organization = Organization(
            name=org_data.name,
            owner_id=owner_id
        )
        
        self.db.add(organization)
        self.db.flush()  # Get the ID without committing
        
        # Create owner membership
        membership = Membership(
            org_id=organization.id,
            user_id=owner_id,
            role="owner"
        )
        
        self.db.add(membership)
        self.db.commit()
        self.db.refresh(organization)
        
        return organization
    
    async def update_organization(self, org_id: str, org_update: OrganizationUpdate) -> Organization:
        """Update organization"""
        organization = self.db.query(Organization).filter(Organization.id == org_id).first()
        
        if not organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        update_data = org_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(organization, field, value)
        
        self.db.commit()
        self.db.refresh(organization)
        
        return organization
    
    async def delete_organization(self, org_id: str) -> None:
        """Delete organization"""
        organization = self.db.query(Organization).filter(Organization.id == org_id).first()
        
        if not organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        self.db.delete(organization)
        self.db.commit()
    
    async def add_member(self, org_id: str, member_data: MembershipCreate) -> Membership:
        """Add member to organization"""
        # Find user by email
        user = self.db.query(User).filter(User.email == member_data.email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if already a member
        existing = self.db.query(Membership).filter(
            Membership.org_id == org_id,
            Membership.user_id == user.id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member"
            )
        
        membership = Membership(
            org_id=org_id,
            user_id=user.id,
            role=member_data.role
        )
        
        self.db.add(membership)
        self.db.commit()
        self.db.refresh(membership)
        
        return membership
    
    async def remove_member(self, org_id: str, user_id: str) -> None:
        """Remove member from organization"""
        membership = self.db.query(Membership).filter(
            Membership.org_id == org_id,
            Membership.user_id == user_id
        ).first()
        
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Membership not found"
            )
        
        # Prevent removing the owner
        if membership.role == "owner":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove organization owner"
            )
        
        self.db.delete(membership)
        self.db.commit()
