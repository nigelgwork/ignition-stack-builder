"""
User stacks management router - CRUD operations for saved stacks
"""

import logging
import uuid
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field, field_serializer
from sqlalchemy.orm import Session

from auth_router import get_current_user
from database import get_db
from models import AuditLog, User, UserStack

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/stacks", tags=["stacks"])


# ======================
# Pydantic Models
# ======================


class StackCreate(BaseModel):
    stack_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    config_json: dict
    is_public: bool = False


class StackUpdate(BaseModel):
    stack_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    config_json: Optional[dict] = None
    is_public: Optional[bool] = None


class StackResponse(BaseModel):
    id: UUID
    user_id: UUID
    stack_name: str
    description: Optional[str]
    config_json: dict
    is_public: bool
    created_at: datetime
    updated_at: datetime
    last_accessed: Optional[datetime]

    @field_serializer("id", "user_id")
    def serialize_uuid(self, value: UUID) -> str:
        """Convert UUID to string for JSON serialization"""
        return str(value)

    class Config:
        from_attributes = True


def log_audit(
    db: Session,
    user_id: str,
    action: str,
    request: Request,
    resource_id: Optional[str] = None,
    details: Optional[dict] = None,
):
    """Log audit event"""
    try:
        audit = AuditLog(
            user_id=user_id,
            action=action,
            resource_type="stack",
            resource_id=resource_id,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            details=details or {},
        )
        db.add(audit)
        db.commit()
    except Exception as e:
        logger.error(f"Audit log error: {e}")


# ======================
# Stack Management Endpoints
# ======================


@router.post("/", response_model=StackResponse, status_code=status.HTTP_201_CREATED)
def create_stack(
    stack_data: StackCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new stack configuration
    """
    try:
        new_stack = UserStack(
            user_id=current_user.id,
            stack_name=stack_data.stack_name,
            description=stack_data.description,
            config_json=stack_data.config_json,
            is_public=stack_data.is_public,
        )

        db.add(new_stack)
        db.commit()
        db.refresh(new_stack)

        # Log creation
        log_audit(
            db,
            str(current_user.id),
            "stack_created",
            request,
            str(new_stack.id),
            {"stack_name": stack_data.stack_name},
        )

        logger.info(f"Stack created: {new_stack.stack_name} by {current_user.email}")
        return new_stack

    except Exception as e:
        db.rollback()
        logger.error(f"Error creating stack: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating stack",
        )


@router.get("/", response_model=List[StackResponse])
def get_user_stacks(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get all stacks for current user
    """
    stacks = (
        db.query(UserStack)
        .filter(UserStack.user_id == current_user.id)
        .order_by(UserStack.updated_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return stacks


@router.get("/{stack_id}", response_model=StackResponse)
def get_stack(
    stack_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a specific stack by ID
    """
    try:
        stack_uuid = uuid.UUID(stack_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid stack ID format"
        )

    stack = (
        db.query(UserStack)
        .filter(UserStack.id == stack_uuid, UserStack.user_id == current_user.id)
        .first()
    )

    if not stack:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Stack not found"
        )

    # Update last accessed
    stack.last_accessed = datetime.utcnow()
    db.commit()

    return stack


@router.put("/{stack_id}", response_model=StackResponse)
def update_stack(
    stack_id: str,
    stack_data: StackUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update a stack configuration
    """
    try:
        stack_uuid = uuid.UUID(stack_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid stack ID format"
        )

    stack = (
        db.query(UserStack)
        .filter(UserStack.id == stack_uuid, UserStack.user_id == current_user.id)
        .first()
    )

    if not stack:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Stack not found"
        )

    try:
        # Update fields if provided
        if stack_data.stack_name is not None:
            stack.stack_name = stack_data.stack_name
        if stack_data.description is not None:
            stack.description = stack_data.description
        if stack_data.config_json is not None:
            stack.config_json = stack_data.config_json
        if stack_data.is_public is not None:
            stack.is_public = stack_data.is_public

        db.commit()
        db.refresh(stack)

        # Log update
        log_audit(
            db,
            str(current_user.id),
            "stack_updated",
            request,
            str(stack.id),
            {"stack_name": stack.stack_name},
        )

        logger.info(f"Stack updated: {stack.stack_name} by {current_user.email}")
        return stack

    except Exception as e:
        db.rollback()
        logger.error(f"Error updating stack: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating stack",
        )


@router.delete("/{stack_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_stack(
    stack_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a stack
    """
    try:
        stack_uuid = uuid.UUID(stack_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid stack ID format"
        )

    stack = (
        db.query(UserStack)
        .filter(UserStack.id == stack_uuid, UserStack.user_id == current_user.id)
        .first()
    )

    if not stack:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Stack not found"
        )

    try:
        stack_name = stack.stack_name
        db.delete(stack)
        db.commit()

        # Log deletion
        log_audit(
            db,
            str(current_user.id),
            "stack_deleted",
            request,
            str(stack_id),
            {"stack_name": stack_name},
        )

        logger.info(f"Stack deleted: {stack_name} by {current_user.email}")

    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting stack: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting stack",
        )


@router.get("/public/list", response_model=List[StackResponse])
def get_public_stacks(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """
    Get public stacks (available to all users)
    """
    stacks = (
        db.query(UserStack)
        .filter(UserStack.is_public == True)
        .order_by(UserStack.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return stacks
