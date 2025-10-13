"""
Authentication router - handles registration, login, MFA, and user management
"""

import logging
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from auth_utils import (create_access_token, create_refresh_token,
                        generate_backup_codes, generate_mfa_qr_code,
                        generate_mfa_secret, generate_verification_token,
                        hash_password, is_valid_email,
                        validate_password_strength, verify_mfa_code,
                        verify_password, verify_token)
from database import get_db
from fastapi import (APIRouter, Depends, HTTPException, Request, Response,
                     status)
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from models import AuditLog, MFABackupCode, RefreshToken, User, UserSettings
from pydantic import BaseModel, EmailStr, Field, field_serializer
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()


# ======================
# Pydantic Models (Request/Response)
# ======================


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class MFAVerify(BaseModel):
    code: str = Field(
        ..., min_length=6, max_length=20
    )  # Support TOTP (6) and backup codes (longer)


class MFASetup(BaseModel):
    enable: bool


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    requires_mfa: bool = False


class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: Optional[str]
    is_active: bool
    is_verified: bool
    mfa_enabled: bool
    created_at: datetime

    @field_serializer("id")
    def serialize_id(self, value: UUID) -> str:
        """Convert UUID to string for JSON serialization"""
        return str(value)

    class Config:
        from_attributes = True


class MFASetupResponse(BaseModel):
    secret: str
    qr_code: str
    backup_codes: list[str]


# ======================
# Helper Functions
# ======================


def log_audit(
    db: Session,
    user_id: Optional[str],
    action: str,
    request: Request,
    details: Optional[dict] = None,
):
    """Log security audit event"""
    try:
        audit = AuditLog(
            user_id=user_id,
            action=action,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            details=details or {},
        )
        db.add(audit)
        db.commit()
    except Exception as e:
        logger.error(f"Audit log error: {e}")


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency to get current authenticated user from JWT token
    """
    token = credentials.credentials
    payload = verify_token(token, token_type="access")

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive"
        )

    return user


# ======================
# Authentication Endpoints
# ======================


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def register(user_data: UserRegister, request: Request, db: Session = Depends(get_db)):
    """
    Register a new user
    """
    # Validate email
    if not is_valid_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email format"
        )

    # Validate password strength
    is_valid, error_msg = validate_password_strength(user_data.password)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)

    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email.lower()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Create new user
    try:
        new_user = User(
            email=user_data.email.lower(),
            password_hash=hash_password(user_data.password),
            full_name=user_data.full_name,
            is_active=True,
            is_verified=False,  # Require email verification in production
            verification_token=generate_verification_token(),
            verification_token_expires=datetime.utcnow() + timedelta(hours=24),
        )

        db.add(new_user)
        db.flush()  # Get the user ID

        # Create default user settings
        user_settings = UserSettings(user_id=new_user.id)
        db.add(user_settings)

        db.commit()
        db.refresh(new_user)

        # Log audit event
        log_audit(db, str(new_user.id), "user_registered", request)

        logger.info(f"New user registered: {new_user.email}")
        return new_user

    except Exception as e:
        db.rollback()
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user account",
        )


@router.post("/login", response_model=TokenResponse)
def login(
    user_data: UserLogin,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    """
    Login and get access token
    """
    # Find user
    user = db.query(User).filter(User.email == user_data.email.lower()).first()

    if not user or not verify_password(user_data.password, user.password_hash):
        # Log failed attempt
        log_audit(db, None, "login_failed", request, {"email": user_data.email})

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive"
        )

    # If MFA is enabled, return temp token requiring MFA
    if user.mfa_enabled:
        temp_token = create_access_token(
            data={"sub": str(user.id), "mfa_pending": True},
            expires_delta=timedelta(minutes=5),
        )
        return TokenResponse(
            access_token=temp_token, refresh_token="", requires_mfa=True
        )

    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    # Store refresh token
    try:
        # Revoke any existing non-revoked refresh tokens for this user to prevent duplicates
        db.query(RefreshToken).filter(
            RefreshToken.user_id == user.id, RefreshToken.revoked == False
        ).update({"revoked": True, "revoked_at": datetime.utcnow()})

        # Commit the revocation first
        db.commit()

        refresh_token_record = RefreshToken(
            user_id=user.id,
            token=refresh_token,
            expires_at=datetime.utcnow() + timedelta(days=7),
        )
        db.add(refresh_token_record)

        # Update last login
        user.last_login = datetime.utcnow()

        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error storing refresh token: {e}")

    # Log successful login
    log_audit(db, str(user.id), "login_success", request)

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/mfa/verify", response_model=TokenResponse)
def verify_mfa(
    mfa_data: MFAVerify,
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """
    Verify MFA code and complete login
    """
    token = credentials.credentials
    payload = verify_token(token, token_type="access")

    if not payload or not payload.get("mfa_pending"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid MFA token"
        )

    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()

    if not user or not user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA not enabled for this user",
        )

    # Verify MFA code
    if not verify_mfa_code(user.mfa_secret, mfa_data.code):
        # Check backup codes
        backup_codes = (
            db.query(MFABackupCode)
            .filter(MFABackupCode.user_id == user.id, MFABackupCode.used == False)
            .all()
        )

        code_valid = False
        for backup_code in backup_codes:
            if verify_password(mfa_data.code, backup_code.code_hash):
                backup_code.used = True
                backup_code.used_at = datetime.utcnow()
                db.commit()
                code_valid = True
                logger.info(f"Backup code used for user: {user.email}")
                break

        if not code_valid:
            log_audit(db, str(user.id), "mfa_failed", request)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid MFA code"
            )

    # Create full access tokens
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    # Store refresh token (revoke old ones first)
    try:
        db.query(RefreshToken).filter(
            RefreshToken.user_id == user.id, RefreshToken.revoked == False
        ).update({"revoked": True, "revoked_at": datetime.utcnow()})

        # Commit revocation first
        db.commit()

        refresh_token_record = RefreshToken(
            user_id=user.id,
            token=refresh_token,
            expires_at=datetime.utcnow() + timedelta(days=7),
        )
        db.add(refresh_token_record)

        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error in MFA verification token storage: {e}")

    # Log successful MFA
    log_audit(db, str(user.id), "mfa_success", request)

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


class RefreshTokenRequest(BaseModel):
    refresh_token: str


@router.post("/refresh", response_model=TokenResponse)
def refresh_access_token(
    token_data: RefreshTokenRequest, db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token
    """
    payload = verify_token(token_data.refresh_token, token_type="refresh")

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    # Check if token exists and is not revoked
    token_record = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.token == token_data.refresh_token,
            RefreshToken.revoked == False,
        )
        .first()
    )

    if not token_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found or revoked",
        )

    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    # Create new access token
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})

    return TokenResponse(
        access_token=access_token, refresh_token=token_data.refresh_token
    )


@router.post("/logout")
def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Logout (revoke refresh tokens)
    """
    try:
        # Revoke all user's refresh tokens
        db.query(RefreshToken).filter(
            RefreshToken.user_id == current_user.id, RefreshToken.revoked == False
        ).update({"revoked": True, "revoked_at": datetime.utcnow()})

        db.commit()

        # Log logout
        log_audit(db, str(current_user.id), "logout", request)

        return {"message": "Successfully logged out"}
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during logout",
        )


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current user information
    """
    return current_user


# ======================
# MFA Endpoints
# ======================


@router.post("/mfa/setup", response_model=MFASetupResponse)
def setup_mfa(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Setup MFA for user (generates secret and QR code)
    """
    if current_user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="MFA is already enabled"
        )

    # Generate MFA secret
    secret = generate_mfa_secret()
    qr_code = generate_mfa_qr_code(current_user.email, secret)

    # Generate backup codes
    backup_codes = generate_backup_codes(count=10)

    # Store secret (not enabled yet - requires verification)
    current_user.mfa_secret = secret
    db.commit()

    # Store backup codes (hashed)
    for code in backup_codes:
        backup_code = MFABackupCode(
            user_id=current_user.id, code_hash=hash_password(code)
        )
        db.add(backup_code)

    db.commit()

    # Log MFA setup
    log_audit(db, str(current_user.id), "mfa_setup_initiated", request)

    return MFASetupResponse(secret=secret, qr_code=qr_code, backup_codes=backup_codes)


@router.post("/mfa/enable")
def enable_mfa(
    mfa_data: MFAVerify,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Enable MFA after verifying a code
    """
    if current_user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="MFA is already enabled"
        )

    if not current_user.mfa_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA not setup. Call /mfa/setup first",
        )

    # Verify the code
    if not verify_mfa_code(current_user.mfa_secret, mfa_data.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid MFA code"
        )

    # Enable MFA
    current_user.mfa_enabled = True
    db.commit()

    # Log MFA enabled
    log_audit(db, str(current_user.id), "mfa_enabled", request)

    return {"message": "MFA enabled successfully"}


@router.post("/mfa/disable")
def disable_mfa(
    mfa_data: MFAVerify,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Disable MFA (requires current MFA code)
    """
    if not current_user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="MFA is not enabled"
        )

    # Verify the code
    if not verify_mfa_code(current_user.mfa_secret, mfa_data.code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid MFA code"
        )

    # Disable MFA
    current_user.mfa_enabled = False
    current_user.mfa_secret = None

    # Delete backup codes
    db.query(MFABackupCode).filter(MFABackupCode.user_id == current_user.id).delete()

    db.commit()

    # Log MFA disabled
    log_audit(db, str(current_user.id), "mfa_disabled", request)

    return {"message": "MFA disabled successfully"}


# ======================
# Password Management
# ======================


@router.post("/password/change")
def change_password(
    password_data: PasswordChange,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Change user password
    """
    # Verify current password
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect",
        )

    # Validate new password
    is_valid, error_msg = validate_password_strength(password_data.new_password)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)

    # Update password
    current_user.password_hash = hash_password(password_data.new_password)
    db.commit()

    # Log password change
    log_audit(db, str(current_user.id), "password_changed", request)

    return {"message": "Password changed successfully"}
