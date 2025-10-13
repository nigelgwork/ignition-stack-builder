"""
User settings management router
"""

import logging
from datetime import datetime
from typing import Optional
from uuid import UUID

from auth_router import get_current_user
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, Request, status
from models import AuditLog, User, UserSettings
from pydantic import BaseModel, field_serializer
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/settings", tags=["settings"])


# ======================
# Pydantic Models
# ======================


class SettingsUpdate(BaseModel):
    preferences: Optional[dict] = None
    theme: Optional[str] = None
    timezone: Optional[str] = None
    notifications_enabled: Optional[bool] = None


class SettingsResponse(BaseModel):
    user_id: UUID
    preferences: dict
    theme: str
    timezone: str
    notifications_enabled: bool
    created_at: datetime
    updated_at: datetime

    @field_serializer("user_id")
    def serialize_user_id(self, value: UUID) -> str:
        """Convert UUID to string for JSON serialization"""
        return str(value)

    class Config:
        from_attributes = True


def log_audit(
    db: Session,
    user_id: str,
    action: str,
    request: Request,
    details: Optional[dict] = None,
):
    """Log audit event"""
    try:
        audit = AuditLog(
            user_id=user_id,
            action=action,
            resource_type="settings",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            details=details or {},
        )
        db.add(audit)
        db.commit()
    except Exception as e:
        logger.error(f"Audit log error: {e}")


# ======================
# Settings Endpoints
# ======================


@router.get("/", response_model=SettingsResponse)
def get_settings(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Get current user's settings
    """
    settings = (
        db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    )

    if not settings:
        # Create default settings if they don't exist
        settings = UserSettings(user_id=current_user.id)
        db.add(settings)
        db.commit()
        db.refresh(settings)

    return settings


@router.put("/", response_model=SettingsResponse)
def update_settings(
    settings_data: SettingsUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update user settings
    """
    settings = (
        db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    )

    if not settings:
        settings = UserSettings(user_id=current_user.id)
        db.add(settings)

    try:
        # Update fields if provided
        if settings_data.preferences is not None:
            settings.preferences = settings_data.preferences
        if settings_data.theme is not None:
            settings.theme = settings_data.theme
        if settings_data.timezone is not None:
            settings.timezone = settings_data.timezone
        if settings_data.notifications_enabled is not None:
            settings.notifications_enabled = settings_data.notifications_enabled

        db.commit()
        db.refresh(settings)

        # Log update
        log_audit(
            db,
            str(current_user.id),
            "settings_updated",
            request,
            {"theme": settings.theme, "timezone": settings.timezone},
        )

        logger.info(f"Settings updated for user: {current_user.email}")
        return settings

    except Exception as e:
        db.rollback()
        logger.error(f"Error updating settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating settings",
        )


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def reset_settings(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Reset settings to default values
    """
    settings = (
        db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    )

    if settings:
        try:
            settings.preferences = {}
            settings.theme = "dark"
            settings.timezone = "UTC"
            settings.notifications_enabled = True

            db.commit()

            # Log reset
            log_audit(db, str(current_user.id), "settings_reset", request)

            logger.info(f"Settings reset for user: {current_user.email}")

        except Exception as e:
            db.rollback()
            logger.error(f"Error resetting settings: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error resetting settings",
            )
